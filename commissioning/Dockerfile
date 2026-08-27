FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY opcua_tool.py fuxa_tool.py binding_plan.py ./
RUN mkdir -p /project/commissioning
COPY tag_intent.json /project/commissioning/tag_intent.json
ENTRYPOINT ["python"]
