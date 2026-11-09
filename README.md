# koplugins

My KOReader plugins as a [ZenPM](https://github.com/xZenLabs/zen-pm) repository.

| Plugin | Description |
| --- | --- |
| [songbook.koplugin](https://github.com/mzimandl/songbook.koplugin) | Songs with guitar chords (ChordPro) and transposition |
| [battleshipswifi.koplugin](https://github.com/mzimandl/battleshipswifi.koplugin) | Battleships (Lodě) for two players over Wi-Fi |
| [backgammonwifi.koplugin](https://github.com/mzimandl/backgammonwifi.koplugin) | Backgammon (Vrchcáby) for two players over Wi-Fi |

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
`plugin_module` is the plugin folder name without `.koplugin`.

- Plugins installed from a branch use `"source_type": "source"` with a `source_url` pointing to the branch zip
  (its top folder is `<repo>-<branch>`, so ZenPM needs `plugin_module` to name the folder).
- Plugins with GitHub releases use `"source_type": "release"` with `source_asset`, the zip attached to each
  release; *Sync versions* writes `versions/<id>.json` and `versions_url`.

## Updates

ZenPM offers an update when `version` in `manifest.json` is greater than `version` in the installed plugin's `_meta.lua`.
The *Sync versions* workflow (`tools/sync_versions.py`; hourly, on a `sync-versions` dispatch from the plugins'
workflows, or right away with `gh workflow run sync-versions.yml -R mzimandl/koplugins`) sets it:

- `source` packages: copied from `_meta.lua` on the branch; bump it there and push.
- `release` packages (Songbook): the newest GitHub release. The newest pre-release (a tag like `v1.3.0-beta.1`)
  goes to `prerelease_version`, which ZenPM offers only with **Beta updates** on in its settings.

## License

[MIT](LICENSE). The plugins listed in `manifest.json` have their own licenses.
