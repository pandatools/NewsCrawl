FROM registry.cn-hangzhou.aliyuncs.com/feapderd/feaplat_worker:2.6
COPY pyproject.toml ./

RUN pip install poetry -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
RUN poetry source add --priority=default mirrors https://pypi.tuna.tsinghua.edu.cn/simple/
RUN poetry install