# 定义变量
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
REQUIREMENTS := requirements.txt

# 定义默认目标
.DEFAULT_GOAL := help

# 安装依赖项
install: $(VENV)/bin/activate
	$(PIP) install -r $(REQUIREMENTS)

# 运行应用程序
run: $(VENV)/bin/activate
	$(PYTHON) main.py

image: $(VENV)/bin/activate
	docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/v-know/chatgpt-telegram-bot:latest --push .

# 显示帮助信息
help:
	@echo "Available targets:"
	@echo "  install   安装依赖项"
	@echo "  run       运行应用程序"