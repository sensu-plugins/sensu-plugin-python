# Change Log
This project adheres to [Semantic Versioning](http://semver.org/).

This CHANGELOG follows the format listed [here](https://github.com/sensu-plugins/community/blob/master/HOW_WE_CHANGELOG.md)

# [Unreleased]

# [0.4.7]
## Added
- handlers can now process commandline arguments (@barryorourke)

# [0.4.5]
## Fixed
- fix read event exception raise (@oboukili)

# [0.4.4]
## Fixed
- Fixes a bug introduced to `utils.config_files` which only returns `/etc/sensu/config.json` (@barryorourke)

# [0.4.3]
## Fixed
- Fixes `utils.config_files` so that it returns a list of files, rather than a list of `None`'s (@barryorourke)

# [0.4.2]
## Fixed
- Fixes `client_name` in `bail()` as it was using an incorrect path within `event` dict (@absolutejam)

# [0.4.1]
## Fixed
- Fixes `get_api_settings` method (@absolutejam)
- Add missing dependeny to setup.py (@barryorourke)

## Changed
- Move utils sub-package into the main package (@barryorourke)

## [0.4.0]
### Added
- Add support for python 3.5, which is the default version in Debian 9. (@barryorourke)
- Added Dockerfiles and docker-compose.yml to aid with local development & testing (@absolutejam)
- Add handler support! (@absolutejam)
- Temporarily drop test coverage percentage (@barryorourke)

## [0.3.2] 2017-10-10
### Fixed
- Variable name changes in the metrics classed missed during the initial 0.3.0 release (@barryorourke)

## [0.3.1] 2017-10-10
### Fixed
- Really obvious logical error introduced whilst making 0.3.0 pass tests (@barryorourke)

## [0.3.0] 2017-10-06
### Breaking Change
- Dropped support for Python 3.3 (@barryorourke)

### Added
- Added ability to submit checks for a jit host (@PhilipHarries)
- Added support for Python 3.6 (@barryorourke)

### Changed
- Update Changelog to comply with standards (@barryorourke)
- Update Ownership in setup.py (@barryorourke)

## [0.2.0] 2014-01-06
- Add support for Python3 (@zsprackett)

## [0.1.0] 2014-01-06
- Initial release (@zsprackett)

[Unreleased]: https://github.com/sensu-plugins/sensu-plugin-python/compare/0.4.7...HEAD
[0.4.7]: https://github.com/sensu-plugins/sensu-plugin-python/compare/0.4.6...0.4.7
[0.4.5]: https://github.com/sensu-plugins/sensu-plugin-python/compare/0.4.5...0.4.6
[0.4.4]: https://github.com/sensu-plugins/sensu-plugin-python/compare/0.4.4...0.4.5
[0.4.3]: https://github.com/sensu-plugins/sensu-plugin-python/compare/0.4.3...0.4.4
[0.4.2]: https://github.com/sensu-plugins/sensu-plugin-python/compare/0.4.2...0.4.3
[0.4.1]: https://github.com/sensu-plugins/sensu-plugin-python/compare/0.4.1...0.4.2
[0.4.1]: https://github.com/sensu-plugins/sensu-plugin-python/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/sensu-plugins/sensu-plugin-python/compare/8920afcda62b34e9134ba9a816582dbf5f52806c...0.4.0
[0.3.2]: https://github.com/sensu-plugins/sensu-plugin-python/compare/40314082947208acf9ed7c6d6c321ea52a14e765...8920afcda62b34e9134ba9a816582dbf5f52806c
[0.3.1]: https://github.com/sensu-plugins/sensu-plugin-python/compare/2deaf3a34cd86afe13af9ab34aefd8056d284e85...40314082947208acf9ed7c6d6c321ea52a14e765
[0.3.0]: https://github.com/sensu-plugins/sensu-plugin-python/compare/1302599c366ce30e04119bbc7551a258b33a7eab...2deaf3a34cd86afe13af9ab34aefd8056d284e85
[0.2.0]: https://github.com/sensu-plugins/sensu-plugin-python/compare/7f3a6311771469ef1a38719a9dfb407f1ff43cf8...1302599c366ce30e04119bbc7551a258b33a7eab
[0.1.0]: https://github.com/sensu-plugins/sensu-plugin-python/commit/7f3a6311771469ef1a38719a9dfb407f1ff43cf8
