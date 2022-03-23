#FROM tensorflow/tensorflow
#FROM pytorch/torchserve as production
FROM pytorch/torchserve

USER 0
RUN apt-get update
#RUN apt-get install vim
RUN apt install unzip

WORKDIR /opt
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip -q awscliv2.zip
RUN sudo ./aws/install

WORKDIR /
RUN mkdir /app
COPY *.py /app/
COPY Common /app/Common
COPY DescriptionProcessing /app/DescriptionProcessing
COPY EnvironmentalImpact /app/EnvironmentalImpact
COPY Projects /app/Projects
COPY RulesEngine /app/RulesEngine
COPY req_docker.txt /app

RUN mkdir /app/models
RUN mkdir /app/models/bert_CV0.1
#COPY models/bert_CV0.1 /app/models/bert_CV0.1
RUN aws s3 cp s3://construction-ai/ajp/models/bert_CV0.1 /app/models/bert_CV0.1/ --recursive

WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r req_docker.txt
ENV FLASK_APP "app:create_app"

EXPOSE 80
COPY entry_point.sh /app
WORKDIR /app
ENTRYPOINT ["sh", "entry_point.sh"]
