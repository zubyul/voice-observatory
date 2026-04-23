// voicedl — API prober for macOS voice downloads via the private
// MobileAsset.framework. This CANNOT trigger downloads from an unsigned
// binary — framework gates queries behind the private entitlement
// com.apple.private.mobileasset.allowed_asset_types. See README.
#import <Foundation/Foundation.h>

@interface MAAssetQuery : NSObject
- (instancetype)initWithType:(NSString *)type;
- (int)queryMetaDataSync;
@property (nonatomic, readonly) NSArray *results;
@end

@interface MAAsset : NSObject
@property (nonatomic, readonly) NSDictionary *attributes;
- (int)startDownload:(NSDictionary *)options andBlockUntilComplete:(BOOL)block;
@end

static NSString * const kVoiceAssetType = @"com.apple.MobileAsset.VoiceServicesVocalizerVoice";

static NSString *displayName(NSDictionary *attrs) {
    for (NSString *k in @[@"VoiceName", @"VoiceDisplayName", @"LocalizedName",
                          @"Voice", @"Name", @"VoiceID", @"VoiceId"]) {
        id v = attrs[k];
        if ([v isKindOfClass:[NSString class]]) return v;
    }
    return @"?";
}
static NSString *localeOf(NSDictionary *attrs) {
    for (NSString *k in @[@"LocalizedLanguage", @"Language",
                          @"LanguageLocaleIdentifier", @"Locale", @"LanguageCode"]) {
        id v = attrs[k];
        if ([v isKindOfClass:[NSString class]]) return v;
    }
    return @"?";
}
static NSString *qualityTag(NSDictionary *attrs) {
    id p = attrs[@"VoiceIsPremium"] ?: attrs[@"Premium"] ?: attrs[@"IsPremium"];
    id e = attrs[@"VoiceIsEnhanced"] ?: attrs[@"Enhanced"] ?: attrs[@"IsEnhanced"];
    if ([p respondsToSelector:@selector(boolValue)] && [p boolValue]) return @"Premium";
    if ([e respondsToSelector:@selector(boolValue)] && [e boolValue]) return @"Enhanced";
    return @"Standard";
}
static void dieUsage(const char *p) {
    fprintf(stderr, "usage:\n"
        "  %s list   [--match SUBSTR]\n"
        "  %s dump   [--limit N]\n"
        "  %s download --name VOICE [--quality Premium|Enhanced]\n", p, p, p);
    exit(64);
}

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc < 2) dieUsage(argv[0]);

        Class qcls = NSClassFromString(@"MAAssetQuery");
        if (!qcls) {
            fprintf(stderr, "error: MAAssetQuery class not available.\n");
            return 2;
        }

        MAAssetQuery *q = [[MAAssetQuery alloc] initWithType:kVoiceAssetType];
        if (!q) { fprintf(stderr, "error: MAAssetQuery init returned nil\n"); return 3; }

        int rc = [q queryMetaDataSync];
        if (rc != 0) {
            fprintf(stderr,
                "queryMetaDataSync rc=%d -- catalog query refused.\n"
                "This is the MobileAsset entitlement gate:\n"
                "  rc=2 ENOENT-like: catalog unreachable without entitlement\n"
                "  rc=5 EACCES-like: asset type not allowed for this caller\n"
                "Apple requires signed callers with\n"
                "  com.apple.private.mobileasset.allowed_asset_types\n"
                "Unsigned binaries cannot trigger downloads directly; use\n"
                "a UI pathway from README.md instead.\n", rc);
        }

        NSArray *results = q.results;
        fprintf(stderr, "%lu voice assets in catalog\n", (unsigned long)results.count);

        NSString *mode = @(argv[1]);
        NSString *match = nil, *nameArg = nil, *qualityArg = nil;
        int limit = 3;
        for (int i = 2; i < argc; i++) {
            NSString *a = @(argv[i]);
            if ([a isEqualToString:@"--match"] && i+1 < argc) match = @(argv[++i]);
            else if ([a isEqualToString:@"--name"] && i+1 < argc) nameArg = @(argv[++i]);
            else if ([a isEqualToString:@"--quality"] && i+1 < argc) qualityArg = @(argv[++i]);
            else if ([a isEqualToString:@"--limit"] && i+1 < argc) limit = atoi(argv[++i]);
        }

        if ([mode isEqualToString:@"list"]) {
            for (MAAsset *a in results) {
                NSDictionary *attrs = a.attributes;
                if (!attrs) continue;
                NSString *dn = displayName(attrs);
                if (match && [dn rangeOfString:match options:NSCaseInsensitiveSearch].location == NSNotFound) continue;
                printf("%-30s %-14s %-8s\n",
                       dn.UTF8String, localeOf(attrs).UTF8String, qualityTag(attrs).UTF8String);
            }
            return 0;
        }
        if ([mode isEqualToString:@"dump"]) {
            int shown = 0;
            for (MAAsset *a in results) {
                if (shown++ >= limit) break;
                NSDictionary *attrs = a.attributes;
                printf("--- asset %d ---\n", shown);
                for (NSString *k in [attrs.allKeys sortedArrayUsingSelector:@selector(compare:)]) {
                    NSString *vs = [attrs[k] description];
                    if (vs.length > 80) vs = [[vs substringToIndex:80] stringByAppendingString:@"..."];
                    printf("  %s = %s\n", k.UTF8String, vs.UTF8String);
                }
            }
            return 0;
        }
        if ([mode isEqualToString:@"download"]) {
            if (!nameArg) { fprintf(stderr, "--name required\n"); return 64; }
            int matched = 0, ok = 0;
            for (MAAsset *a in results) {
                NSDictionary *attrs = a.attributes;
                NSString *dn = displayName(attrs);
                if ([dn caseInsensitiveCompare:nameArg] != NSOrderedSame) continue;
                if (qualityArg && ![qualityTag(attrs) isEqualToString:qualityArg]) continue;
                matched++;
                fprintf(stderr, "downloading: %s (%s)\n", dn.UTF8String, qualityTag(attrs).UTF8String);
                int drc = [a startDownload:@{} andBlockUntilComplete:YES];
                fprintf(stderr, "  rc=%d\n", drc);
                if (drc == 0) ok++;
            }
            fprintf(stderr, "matched=%d ok=%d\n", matched, ok);
            return ok > 0 ? 0 : 1;
        }
        dieUsage(argv[0]);
    }
    return 0;
}
