#import <Foundation/Foundation.h>
int main(int argc, char **argv) {
    @autoreleasepool {
        fprintf(stderr,
            "voicedl - stub for macOS voice install via private MobileAsset.framework\n\n"
            "This CLI cannot download voices. The private framework is gated by\n"
            "  com.apple.private.mobileasset.allowed_asset_types\n"
            "held only by Apple-signed system components (Settings.app, sharingd,\n"
            "mobileassetd, softwareupdated). Earlier iterations segfaulted (ARC +\n"
            "dynamic NSInvocation) or failed to link ObjC class symbols from the\n"
            "private framework without Apple SDK headers.\n\n"
            "To download voices use a UI pathway:\n"
            "  open 'x-apple.systempreferences:com.apple.Accessibility-Settings.extension?Spoken Content'\n"
            "  open '/System/Library/CoreServices/VoiceOver Utility.app'\n\n"
            "See README.md and voice_observatory.py for the full picture.\n");
        (void)argc; (void)argv;
    }
    return 0;
}
