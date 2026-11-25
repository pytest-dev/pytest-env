With `env_files_skip_if_set = true`, variables set by an earlier `env_files` entry count as existing when later files load: the first file wins, and `${VAR}` references expand to the kept value.
