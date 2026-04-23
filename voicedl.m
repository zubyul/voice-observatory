// voicedl — fetch additional macOS TTS voices via MobileAsset private framework.
//
// Usage:
//   voicedl list [--match SUBSTR]
//   voicedl dump [--limit N]          ;; print attribute keys of first N assets
//   voicedl download --name VOICE [--quality Premium|Enhanced]
//
// NOTE: uses Apples /System/Library/PrivateFrameworks/MobileAsset.framework.
// Class names + selectors here are stable across recent macOS but are NOT
// public API; verify with `voicedl dump` before scripting against them.
//
// Build: clang -framework Foundation -o voicedl voicedl.m
#import <Foundation/Foundation.h>

@interface DynamicQuery : NSObject
@end
@implementation DynamicQuery
@end

static NSString * const kVoiceAssetType = @"com.apple.MobileAsset.VoiceServicesVocalizerVoice";

static id allocQuery(Class qcls) {
    id q = [qcls alloc];
    SEL initSel = @selector(initWithType:);
    NSMethodSignature *sig = [q methodSignatureForSelector:initSel];
    if (!sig) return nil;
    NSInvocation *inv = [NSInvocation invocationWithMethodSignature:sig];
    [inv setSelector:initSel];
    [inv setTarget:q];
    NSString *t = kVoiceAssetType;
    [inv setArgument:&t atIndex:2];
    [inv invoke];
    id out = nil;
    [inv getReturnValue:&out];
    return out;
}

static int runSync(id q) {
    SEL s = @selector(queryMetaDataSync);
    NSMethodSignature *sig = [q methodSignatureForSelector:s];
    if (!sig) return -1;
    NSInvocation *inv = [NSInvocation invocationWithMethodSignature:sig];
    [inv setSelector:s]; [inv setTarget:q]; [inv invoke];
    int rc = 0; [inv getReturnValue:&rc];
    return rc;
}

static int downloadAsset(id asset) {
    SEL s = @selector(startDownload:andBlockUntilComplete:);
    NSMethodSignature *sig = [asset methodSignatureForSelector:s];
    if (!sig) return -1;
    NSInvocation *inv = [NSInvocation invocationWithMethodSignature:sig];
    [inv setSelector:s]; [inv setTarget:asset];
    NSDictionary *opts = @{};
    BOOL block = YES;
    [inv setArgument:&opts atIndex:2];
    [inv setArgument:&block atIndex:3];
    [inv invoke];
    int rc = 0; [inv getReturnValue:&rc];
    return rc;
}

static NSString *displayName(NSDictionary *attrs) {
    for (NSString *k in @[@"VoiceName", @"VoiceDisplayName", @"LocalizedName",
                          @"Voice", @"Name"]) {
        id v = attrs[k];
        if ([v isKindOfClass:[NSString class]]) return (NSString *)v;
    }
    return @"?";
}

static NSString *qualityTag(NSDictionary *attrs) {
    id p = attrs[@"VoiceIsPremium"] ?: attrs[@"Premium"];
    id e = attrs[@"VoiceIsEnhanced"] ?: attrs[@"Enhanced"];
    if ([p respondsToSelector:@selector(boolValue)] && [p boolValue]) return @"Premium";
    if ([e respondsToSelector:@selector(boolValue)] && [e boolValue]) return @"Enhanced";
    return @"Standard";
}

static void dieUsage(const char *prog) {
    fprintf(stderr,
        "usage:\n"
        "  %s list   [--match SUBSTR]\n"
        "  %s dump   [--limit N]\n"
        "  %s download --name VOICE [--quality Premium|Enhanced]\n",
        prog, prog, prog);
    exit(64);
}

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc < 2) dieUsage(argv[0]);

        NSBundle *b = [NSBundle bundleWithPath:@"/System/Library/PrivateFrameworks/MobileAsset.framework"];
        if (!b || ![b load]) { fprintf(stderr, "error: failed to load MobileAsset.framework\n"); return 2; }

        Class qcls = NSClassFromString(@"MAAssetQuery");
        if (!qcls) { fprintf(stderr, "error: MAAssetQuery class not found (API changed?)\n"); return 3; }

        id q = allocQuery(qcls);
        if (!q) { fprintf(stderr, "error: -initWithType: unavailable\n"); return 4; }

        int rc = runSync(q);
        if (rc != 0) fprintf(stderr, "warning: queryMetaDataSync rc=%d\n", rc);

        NSArray *results = [q valueForKey:@"results"];
        fprintf(stderr, "%lu voice assets in catalog\n", (unsigned long)results.count);

        NSString *mode = @(argv[1]);
        NSString *match = nil, *nameArg = nil, *qualityArg = nil;
        int limit = 3;
        for (int i = 2; i < argc; i++) {
            NSString *a = @(argv[i]);
            if ([a isEqualToString:@"--match"]  && i+1 < argc) match      = @(argv[++i]);
            else if ([a isEqualToString:@"--name"]    && i+1 < argc) nameArg   = @(argv[++i]);
            else if ([a isEqualToString:@"--quality"] && i+1 < argc) qualityArg= @(argv[++i]);
            else if ([a isEqualToString:@"--limit"]   && i+1 < argc) limit     = atoi(argv[++i]);
        }

        if ([mode isEqualToString:@"list"]) {
            for (id asset in results) {
                NSDictionary *attrs = [asset valueForKey:@"attributes"];
                if (!attrs) continue;
                NSString *dn = displayName(attrs);
                if (match && [dn rangeOfString:match options:NSCaseInsensitiveSearch].location == NSNotFound) continue;
                NSString *lang = attrs[@"LocalizedLanguage"] ?: attrs[@"Language"] ?: attrs[@"LanguageLocaleIdentifier"] ?: @"?";
                printf("%-30s %-12s %-8s\n", dn.UTF8String, ((NSString *)lang).UTF8String, qualityTag(attrs).UTF8String);
            }
            return 0;
        }
        if ([mode isEqualToString:@"dump"]) {
            int shown = 0;
            for (id asset in results) {
                if (shown++ >= limit) break;
                NSDictionary *attrs = [asset valueForKey:@"attributes"];
                printf("---\n");
                for (NSString *k in [attrs.allKeys sortedArrayUsingSelector:@selector(compare:)]) {
                    printf("  %s = %s\n", k.UTF8String, [[attrs[k] description] UTF8String]);
                }
            }
            return 0;
        }
        if ([mode isEqualToString:@"download"]) {
            if (!nameArg) { fprintf(stderr, "--name required\n"); return 64; }
            int matched = 0, ok = 0;
            for (id asset in results) {
                NSDictionary *attrs = [asset valueForKey:@"attributes"];
                NSString *dn = displayName(attrs);
                if ([dn caseInsensitiveCompare:nameArg] != NSOrderedSame) continue;
                if (qualityArg && ![qualityTag(attrs) isEqualToString:qualityArg]) continue;
                matched++;
                fprintf(stderr, "downloading: %s (%s)\n", dn.UTF8String, qualityTag(attrs).UTF8String);
                int drc = downloadAsset(asset);
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
