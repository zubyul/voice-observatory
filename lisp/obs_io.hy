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

(setv BAG-HAIKUS
  {"X"  ["Between two forests"
         "Lekha, Isha, Rishi stand --"
         "a single shore rises"]
   "D0" ["Rivers born of snow"
         "Equations beneath starlight --"
         "silence asks the form"]
   "E"  ["Three scripts at the door --"
         "Cyrillic, Aleph, Alef --"
         "each breath a new sun"]
   "F"  ["Rhythm across mountains"
         "Devanagari meets Farsi --"
         "prime numbers, whispered"]
   "G"  ["Islands speak in tones"
         "Thai, Vietnamese, Indonesian --"
         "truth grows like new rain"]
   "C1_prime" ["Li Shanlan in Qing"
               "Chang's curvature, Chern's forms --"
               "centuries fold flat"]})

(defn get-bag-haiku [bag-name]
  (get BAG-HAIKUS bag-name None))

(defn bag-haiku-items []
  "Return a plain Python list of (name, lines) tuples sorted by name."
  (sorted (.items BAG-HAIKUS)))
