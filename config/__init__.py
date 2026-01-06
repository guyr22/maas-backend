from envyaml import EnvYAML

CONFIG_YAML_FILE = "config.yaml"


class MockConfig(dict):
    def __getitem__(self, key):
        if "." in key:
            keys = key.split(".")
            val = self
            for k in keys:
                val = val[k]
            return val
        return super().__getitem__(key)


try:
    config = EnvYAML(f"config/{CONFIG_YAML_FILE}")
except Exception as e:
    print(f"Config loading failed: {e}. Using dummy config.")
    config = MockConfig(
        {
            "db": {"connection_string": "mongodb://localhost:27017"},
            "security": {"secret_key": "Rm-mI8wi4GFbOU33MxusA8UYVjNU8NSUyNx68Uvfh2E="},
            "kafka": {
                "servers": ["localhost:9092"],
                "topic": "test",
                "security_protocol": "SASL_PLAINTEXT",
                "sasl_mechanism": "PLAIN",
                "sasl_username": "u",
                "sasl_password": "p",
            },
            "logs": {
                "base_level": "DEBUG",
                "level": "DEBUG",
                "console_format": "%(message)s",
                "console": {"level": "DEBUG", "format": "%(message)s"},
                "logstash": {
                    "enable": False,
                    "enabled": False,
                    "host": "localhost",
                    "port": 5000,
                    "version": 1,
                },
            },
        }
    )
