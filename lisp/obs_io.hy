;; obs_io.hy — Hy inner layer: subprocess + filesystem + data-only helpers.
;; Exposes plain-Python data (dict / list / str) for Basilisp to consume.

(import subprocess os re json)

(setv ASSET-DIR
  "/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_VoiceServicesVocalizerVoice")

(defn voices-raw []
  (try
    (-> (subprocess.check_output ["say" "-v" "?"] :text True :timeout 2)
        (.splitlines))
    (except [e Exception] [])))

(defn parse-voice-line [line]
  (setv m (re.match r"^([^#]+?)\s+[a-z]{2}[_A-Z]*(?:@[^#]*)?\s*#" line))
  (when m
    {"name" (.strip (.group m 1))
     "premium" (in "(Premium)" line)
     "enhanced" (in "(Enhanced)" line)}))

(defn parse-voices []
  "Return a list of {name, premium, enhanced} dicts for installed voices."
  (lfor line (voices-raw)
        :setv v (parse-voice-line line)
        :if v
        v))

(defn installed-names []
  "Return a plain Python list of voice name strings."
  (lfor v (parse-voices) (get v "name")))

(defn asset-count []
  (try (len (os.listdir ASSET-DIR))
       (except [e FileNotFoundError] 0)))

(defn load-neighbors [[path "voice-neighbors.json"]]
  (with [f (open path "r")] (json.load f)))
