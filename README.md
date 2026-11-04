# koplugins

My KOReader plugins as a [ZenPM](https://github.com/xZenLabs/zen-pm) repository.

| Plugin | Description |
| --- | --- |
| [songbook.koplugin](https://github.com/mzimandl/songbook.koplugin) | Songs with guitar chords (ChordPro) and transposition |
| [battleships.koplugin](https://github.com/mzimandl/battleships.koplugin) | Battleships for two players over Wi-Fi |

## Adding the repository to ZenPM

Add this URL in ZenPM → Sources:

```
https://raw.githubusercontent.com/mzimandl/koplugins/master/
```

or from the command line:

```
zenpm repo add mzimandl https://raw.githubusercontent.com/mzimandl/koplugins/master/
```

## Adding a plugin

Add an entry to `packages` in `manifest.json` (format: [repository-index contract](https://github.com/xZenLabs/zen-pm/blob/main/docs/architecture/repository-index.md)).
Plugins without GitHub releases use `"source_type": "source"` with a `source_url` pointing to the branch zip;
`plugin_module` is the plugin folder name without `.koplugin` (the zip's top folder is `<repo>-<branch>`, so ZenPM needs it to name the folder).

## Updates

ZenPM offers an update when `version` in `manifest.json` is greater than `version` in the installed plugin's `_meta.lua`.
To release a new build, bump `version` in the plugin's `_meta.lua` and push it; the *Sync versions* workflow
copies it into `manifest.json` (hourly, or right away with `gh workflow run sync-versions.yml -R mzimandl/koplugins`).
