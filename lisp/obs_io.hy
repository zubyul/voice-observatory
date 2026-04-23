;; obs_io.hy — Hy inner layer: subprocess + filesystem helpers.
;; Returns plain Python data (dict / list / str) for Basilisp.

(import subprocess os re json)

(setv ASSET-DIR
  "/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_VoiceServicesVocalizerVoice")

(defn voices-raw []
  (try
    (.splitlines
      (subprocess.check_output ["say" "-v" "?"] :text True :timeout 2))
    (except [e Exception] [])))

(defn parse-voice-line [line]
  (setv m (re.match r"^([^#]+?)\s+[a-z]{2}[_A-Z]*(?:@[^#]*)?\s*#" line))
  (when m
    {"name" (.strip (.group m 1))
     "premium" (in "(Premium)" line)
     "enhanced" (in "(Enhanced)" line)}))

(defn parse-voices []
  (setv out [])
  (for [line (voices-raw)]
    (setv v (parse-voice-line line))
    (when v (.append out v)))
  out)

(defn installed-names []
  (setv out [])
  (for [v (parse-voices)]
    (.append out (get v "name")))
  out)

(defn asset-count []
  (try (len (os.listdir ASSET-DIR))
       (except [e FileNotFoundError] 0)))

(defn load-neighbors [[path "voice-neighbors.json"]]
  (with [f (open path "r")]
    (json.load f)))

(defn say-narrate [text [voice "Fiona (Enhanced)"]]
  "Pipe a string through macOS say with a given voice.
   Blocks until narration completes."
  (subprocess.run ["say" "-v" voice text] :check False))
