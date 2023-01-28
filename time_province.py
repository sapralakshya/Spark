import argparse
from uuid import uuid4
from six.moves import input
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
import pandas as pd
from typing import List
FILE_PATH= "C:/Users/91829/Desktop/Spark/Spark_datasets/TimeProvince.csv"
coloumns=['date','time','province','confirmed','released','deceased']

API_KEY='2MMDHYDOO2U6CDAM'
API_SECRET_KEY='a3b5bCtL88rLmjl4md/7jVxYjg8JmRdZwtYM5PPTOHT30DNiSVVz0u5YBHBfdpcW'
ENDPOINT_SCHEMA_URL='https://psrc-vn38j.us-east-2.aws.confluent.cloud'
BOOTSTRAP_SERVER='pkc-l7pr2.ap-south-1.aws.confluent.cloud:9092'
SECURITY_PROTOCOL='SASL_SSL'
SSL_MECHANISM='PLAIN'
SCHEMA_REGISTRY_API_KEY='7G4R5WMSAH7MWXY2'
SCHEMA_REGISTRY_API_SECRET='rqfpVVdualMNj41t+mTGq3ndflJ1svvH/97edUsOrwg5x9at+tEIzlDPywUankrQ'
def sasl_conf():
    sasl_conf= {'sasl.mechanism': SSL_MECHANISM,'bootstrap.servers': BOOTSTRAP_SERVER,'security.protocol': SECURITY_PROTOCOL,'sasl.username': API_KEY,'sasl.password': API_SECRET_KEY,'queue.buffering.max.messages':1100000}
    return sasl_conf
def schema_config():
    return {'url':ENDPOINT_SCHEMA_URL, 'basic.auth.user.info':f"{SCHEMA_REGISTRY_API_KEY}:{SCHEMA_REGISTRY_API_SECRET}"
           }
class Case:
    def __init__(self,value:dict):
        for k,v in value.items():
            setattr(self,k,v)
        self.value=value
    @staticmethod
    def dict_to_case(data:dict,ctx):
        return Case(value=data)
    def __str__(self):
        return f"{self.value}"

def get_case_data(file_path):
    df=pd.read_csv(file_path)
    df=df.iloc[:,0:]
    df=df.fillna("Nan")
    cases:List[Case]=[]
    for i in df.values:
        case=Case(dict(zip(coloumns,i)))
        cases.append(case)
        yield case
def case_to_dict(case:Case,ctx):
    return case.value
def delivery_report(err, msg):
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))
def main(topic):
    schema_str = """
     {
  "$id": "http://example.com/myURI.schema.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "additionalProperties": false,
  "description": "Sample schema to help you get started.",
  "properties": {
    "date": {
      "description": "The type(v) type is used.",
      "type": "string"
    },
    "time": {
      "description": "The type(v) type is used.",
      "type": "number"
    },
    "province": {
      "description": "The type(v) type is used.",
      "type": "string"
    },
    "confirmed": {
      "description": "The type(v) type is used.",
      "type": "number"
    },
    "released": {
      "description": "The type(v) type is used.",
      "type": "number"
    },
    "deceased": {
      "description": "The type(v) type is used.",
      "type": "number"
    }
  },
  "title": "SampleRecord",
  "type": "object"
}
    """
    schema_registry_conf=schema_config()
    schema_registry_client=SchemaRegistryClient(schema_registry_conf)
    string_serializer= StringSerializer('utf8')
    json_serializer=JSONSerializer(schema_str,schema_registry_client,case_to_dict)
    producer= Producer(sasl_conf())
    print("Producing values to topic{}".format(topic))
    producer.poll(0.0)
    try:
       for  case in  get_case_data(file_path=FILE_PATH):
           print(case)
           producer.produce(topic=topic,key=string_serializer(str(uuid4()),case_to_dict),value=json_serializer(case,SerializationContext(topic,MessageField.VALUE)),on_delivery=delivery_report)
    except KeyboardInterrupt:
        pass
    except ValueError:
        print("Invalid input, discarding record....")
        pass
    print("Flushing records...")
    producer.flush(50)
main("time_province")








