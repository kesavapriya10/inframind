import json
import flask
from flask import render_template, request, url_for
import boto3
import botocore
app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return render_template('./home.html')

@app.route('/data', methods=['POST'])
def data():

    client = boto3.client('cloudformation',region_name = "",aws_access_key_id="",
        aws_secret_access_key="")

    template = {
    "AWSTemplateFormatVersion" : "2010-09-09",
  
    "Description" : "",
    "Parameters" : {

      "InstanceType" : {
        "Description" : "",
        "ConstraintDescription" : "must be a valid EC2 instance type.",
        "Type" : "String",
        "Default" : "",
        "AllowedValues" : ["t2.micro","t2.nano"]
      },
  
      "KeyName" : {
        "Description" : "The EC2 Key Pair to allow SSH access to the instances",
        "ConstraintDescription" : "must be the name of an existing EC2 KeyPair.",
        "Type" : "String",
        "Default":""
        
      },
  
      "SSHLocation" : {
        "Description" : "The IP address range that can be used to SSH to the EC2 instances",
        "ConstraintDescription": "must be a valid IP CIDR range of the form x.x.x.x/x.",
        "Type": "String",
        "Default": "",
        "MinLength": "9",
        "MaxLength": "18",
        "AllowedPattern": "(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})"
      },
       "DBName" : {
        "Default": "wordpressdb",
        "Description" : "The WordPress database name",
        "ConstraintDescription" : "must begin with a letter and contain only alphanumeric characters.",
        "Type": "String",
        "MinLength": "1",
        "MaxLength": "64",
        "AllowedPattern" : "[a-zA-Z][a-zA-Z0-9]*"
        
      },
  
      "DBUser" : {
        "Description" : "The WordPress database admin account username",
        "ConstraintDescription" : "must begin with a letter and contain only alphanumeric characters.",
        "Type": "String",
        "Default":"wordpress",
        "NoEcho": "true"
        
        
      },
  
      "DBPassword" : {
        "Description" : "The WordPress database admin account password",
        "ConstraintDescription" : "must contain only alphanumeric characters.",
        "Type": "String",
        "Default":"",
        "NoEcho": "true"
        
        
        
      },
  
      "DBRootPassword" : {
        "Description" : "MySQL root password",
        "ConstraintDescription" : "must contain only alphanumeric characters.",
        "Type": "String",
        "Default":"admin",
        "NoEcho": "true"
      }
    },
  
    "Mappings" : {
      "AWSInstanceType2Arch" : {
        "t1.micro"    : { "Arch" : "HVM64"  },
        "t2.nano"     : { "Arch" : "HVM64"  },
        "t2.micro"    : { "Arch" : "HVM64"  },
        "t2.small"    : { "Arch" : "HVM64"  },
        "t2.medium"   : { "Arch" : "HVM64"  },
        "t2.large"    : { "Arch" : "HVM64"  }
      },
  
      "AWSInstanceType2NATArch" : {
        "t1.micro"    : { "Arch" : "NATHVM64"  },
        "t2.nano"     : { "Arch" : "NATHVM64"  },
        "t2.micro"    : { "Arch" : "NATHVM64"  },
        "t2.small"    : { "Arch" : "NATHVM64"  },
        "t2.medium"   : { "Arch" : "NATHVM64"  },
        "t2.large"    : { "Arch" : "NATHVM64"  }
      }
  ,
      "AWSRegionArch2AMI" : {
        "ap-northeast-3"   : {"HVM64" : "ami-01344f6f63a4decc1", "HVMG2" : "NOT_SUPPORTED"},
        "ap-south-1"       : {"HVM64" : "ami-03cfb5e1fb4fac428", "HVMG2" : "ami-0244c1d42815af84a"},
        "ap-southeast-1"   : {"HVM64" : "ami-0ba35dc9caf73d1c7", "HVMG2" : "ami-0e46ce0d6a87dc979"},
        "ap-southeast-2"   : {"HVM64" : "ami-0ae99b503e8694028", "HVMG2" : "ami-0c0ab057a101d8ff2"},
         "af-south-1"       : {"HVM64" : "ami-064cc455f8a1ef504", "HVMG2" : "NOT_SUPPORTED"},
        "ap-east-1"        : {"HVM64" : "ami-f85b1989", "HVMG2" : "NOT_SUPPORTED"},
        "ap-northeast-1"   : {"HVM64" : "ami-0b2c2a754d5b4da22", "HVMG2" : "ami-09d0e0e099ecabba2"},
        "ap-northeast-2"   : {"HVM64" : "ami-0493ab99920f410fc", "HVMG2" : "NOT_SUPPORTED"}
        
      }
  
    },
   
    "Resources" : {
  
      "WebServer" : {
        "Type" : "AWS::AutoScaling::AutoScalingGroup",
        "Properties" : {
          "AvailabilityZones" : { "Fn::GetAZs" : ""},
          "LaunchConfigurationName" : { "Ref" : "LaunchConfig" },
          "LoadBalancerNames" : [ { "Ref" : "ElasticLB" } ],
          "MinSize" : "1",
          "MaxSize" : "3"
        },
        "CreationPolicy" : {
          "ResourceSignal" : {
            "Timeout" : "PT15M",
            "Count"   : "1"
          }
        },
        "UpdatePolicy": {
          "AutoScalingRollingUpdate": {
            "MinInstancesInService": "1",
            "MaxBatchSize": "1",
            "PauseTime" : "PT15M",
            "WaitOnResourceSignals": "true"
          }
        }
      },
  
      "LaunchConfig" : {
        "Type" : "AWS::AutoScaling::LaunchConfiguration",
        "Metadata" : {
          "Comment" : "Install a simple application",
          "AWS::CloudFormation::Init" : {
            "config" : {
              "packages" : {
                "yum" : {
                  "php73"          : [],
                  "php73-mysqlnd"  : [],
                  "mysql57-devel"  : [],
                  "mysql57-libs"   : [],
                  "httpd24"        : []
                }
              },
              "sources" : {
                "/var/www/html" : "http://wordpress.org/latest.tar.gz"
              },
              "files" : {
                "/var/www/html/index.html" : {
                  "content" : { "Fn::Join" : ["\n", [
                    "<h1>Congratulations, you have successfully launched the AWS CloudFormation sample.</h1>"
                  ]]},
                  "mode"    : "000644",
                  "owner"   : "root",
                  "group"   : "root"
                },
  
                 "/tmp/create-wp-config" : {
                  "content" : { "Fn::Join" : [ "", [
                    "#!/bin/bash\n",
                    "cp /var/www/html/wordpress/wp-config-sample.php /var/www/html/wordpress/wp-config.php\n",
                    "sed -i \"s/'database_name_here'/'",{ "Ref" : "DBName" }, "'/g\" wp-config.php\n",
                    "sed -i \"s/'username_here'/'",{ "Ref" : "DBUser" }, "'/g\" wp-config.php\n",
                    "sed -i \"s/'password_here'/'",{ "Ref" : "DBPassword" }, "'/g\" wp-config.php\n",
                    "sed -i \"s/'localhost'/'",{ "Fn::GetAtt" : [ "DBInstance", "PublicIp" ] }, "'/g\" wp-config.php\n"
                  ]]},
                  "mode" : "000500",
                  "owner" : "root",
                  "group" : "root"
                },
                "/etc/cfn/cfn-hup.conf" : {
                  "content" : { "Fn::Join" : ["", [
                    "[main]\n",
                    "stack=", { "Ref" : "AWS::StackId" }, "\n",
                    "region=", { "Ref" : "AWS::Region" }, "\n"
                  ]]},
                  "mode"    : "000400",
                  "owner"   : "root",
                  "group"   : "root"
                },
  
                "/etc/cfn/hooks.d/cfn-auto-reloader.conf" : {
                  "content": { "Fn::Join" : ["", [
                    "[cfn-auto-reloader-hook]\n",
                    "triggers=post.update\n",
                    "path=Resources.LaunchConfig.Metadata.AWS::CloudFormation::Init\n",
                    "action=/opt/aws/bin/cfn-init -v ",
                    "         --stack ", { "Ref" : "AWS::StackName" },
                    "         --resource LaunchConfig",
                    "         --region ", { "Ref" : "AWS::Region" }, "\n",
                    "runas=root\n"
                  ]]}
                }
              },
              "commands" : {
                "01_configure_wordpress" : {
                  "command" : "/tmp/create-wp-config",
                  "cwd" : "/var/www/html/wordpress"
                }
              },
              "services" : {
                "sysvinit" : {
                  "httpd"    : { "enabled" : "true", "ensureRunning" : "true" },
                  "cfn-hup" : { "enabled" : "true", "ensureRunning" : "true",
                                "files" : ["/etc/cfn/cfn-hup.conf", "/etc/cfn/hooks.d/cfn-auto-reloader.conf"]}
                }
              }
            }
          }
        },
        "Properties" : {
          "KeyName" : { "Ref" : "KeyName" },
          "ImageId" : { "Fn::FindInMap" : [ "AWSRegionArch2AMI", { "Ref" : "AWS::Region" },
                                            { "Fn::FindInMap" : [ "AWSInstanceType2Arch", { "Ref" : "InstanceType" }, "Arch" ] } ] },
          "SecurityGroups" : [ { "Ref" : "WordpressInstanceSecurityGroup" } ],
          "InstanceType" : { "Ref" : "InstanceType" },
          "UserData"       : { "Fn::Base64" : { "Fn::Join" : ["", [
               "#!/bin/bash -xe\n",
               "yum update -y aws-cfn-bootstrap\n",
  
               "/opt/aws/bin/cfn-init -v ",
               "         --stack ", { "Ref" : "AWS::StackName" },
               "         --resource LaunchConfig",
               "         --region ", { "Ref" : "AWS::Region" }, "\n",
  
               "/opt/aws/bin/cfn-signal -e $? ",
               "         --stack ", { "Ref" : "AWS::StackName" },
               "         --resource WebServer ",
               "         --region ", { "Ref" : "AWS::Region" }, "\n"
          ]]}}
        }
      },
  
      "ServerScaleUpPolicy" : {
        "Type" : "AWS::AutoScaling::ScalingPolicy",
        "Properties" : {
          "AdjustmentType" : "ChangeInCapacity",
          "AutoScalingGroupName" : { "Ref" : "WebServer" },
          "Cooldown" : "60",
          "ScalingAdjustment" : "1"
        }
      },
      "ServerScaleDownPolicy" : {
        "Type" : "AWS::AutoScaling::ScalingPolicy",
        "Properties" : {
          "AdjustmentType" : "ChangeInCapacity",
          "AutoScalingGroupName" : { "Ref" : "WebServer" },
          "Cooldown" : "60",
          "ScalingAdjustment" : "-1"
        }
      },
  
      "ProcessAlarmHigh": {
       "Type": "AWS::CloudWatch::Alarm",
       "Properties": {
          "AlarmDescription": "Scale-up if CPU > 70% for 10 minutes",
          "MetricName": "CPUUtilization",
          "Namespace": "AWS/EC2",
          "Statistic": "Average",
          "Period": "300",
          "EvaluationPeriods": "2",
          "Threshold": "70",
          "AlarmActions": [ { "Ref": "ServerScaleUpPolicy" } ],
          "Dimensions": [
            {
              "Name": "AutoScalingGroupName",
              "Value": { "Ref": "WebServer" }
            }
          ],
          "ComparisonOperator": "GreaterThanThreshold"
        }
      },
      "ProcessAlarmLow": {
       "Type": "AWS::CloudWatch::Alarm",
       "Properties": {
          "AlarmDescription": "Scale-down if CPU < 70% for 10 minutes",
          "Statistic": "Average",
          "Namespace": "AWS/EC2",
          "Period": "300",
          "EvaluationPeriods": "2",
          "Threshold": "70",
          "MetricName": "CPUUtilization",
          "AlarmActions": [ { "Ref": "ServerScaleDownPolicy" } ],
          "Dimensions": [
            {
              "Name": "AutoScalingGroupName",
              "Value": { "Ref": "WebServer" }
            }
          ],
          "ComparisonOperator": "LessThanThreshold"
        }
      },
  
      "ElasticLB" : {
        "Type" : "AWS::ElasticLoadBalancing::LoadBalancer",
        "Properties" : {
          "AvailabilityZones" : { "Fn::GetAZs" : "" },
          "CrossZone" : "true",
          "Listeners" : [ {
            "LoadBalancerPort" : "80",
            "InstancePort" : "80",
            "Protocol" : "HTTP"
          } ],
          "HealthCheck" : {
            "Target" : "HTTP:80/",
            "HealthyThreshold" : "3",
            "UnhealthyThreshold" : "5",
            "Interval" : "30",
            "Timeout" : "5"
          }
        }
      },
  
      "WordpressInstanceSecurityGroup" : {
        "Type" : "AWS::EC2::SecurityGroup",
        "Properties" : {
          "GroupDescription" : "Enable SSH access and HTTP from the load balancer only",
          "SecurityGroupIngress" : [ {
            "IpProtocol" : "tcp",
            "FromPort" : "22",
            "ToPort" : "22",
            "CidrIp" : { "Ref" : "SSHLocation"}
          },
          {
            "IpProtocol" : "tcp",
            "FromPort" : "80",
            "ToPort" : "80",
            "SourceSecurityGroupOwnerId" : {"Fn::GetAtt" : ["ElasticLB", "SourceSecurityGroup.OwnerAlias"]},
            "SourceSecurityGroupName" : {"Fn::GetAtt" : ["ElasticLB", "SourceSecurityGroup.GroupName"]}
          } ]
        }
      },
      "DBSecurityGroup" : {
        "Type" : "AWS::EC2::SecurityGroup",
        "Properties" : {
          "GroupDescription" : "Enable HTTP access via port 80 locked down to the load balancer + SSH access",
          "SecurityGroupIngress" : [
            {"IpProtocol" : "tcp", "FromPort" : "3306", "ToPort" : "3306", "CidrIp" : "0.0.0.0/0"},
            {"IpProtocol" : "tcp", "FromPort" : "22", "ToPort" : "22", "CidrIp" : { "Ref" : "SSHLocation"}}
          ]
        }
      },
      "DBInstance": {
      "Type": "AWS::EC2::Instance",
      "Properties": {
          "KeyName" : { "Ref" : "KeyName" },
          "ImageId" : { "Fn::FindInMap" : [ "AWSRegionArch2AMI", { "Ref" : "AWS::Region" },
                                            { "Fn::FindInMap" : [ "AWSInstanceType2Arch", { "Ref" : "InstanceType" }, "Arch" ] } ] },
          "InstanceType" : { "Ref" : "InstanceType" },
          "SecurityGroups" : [ {"Ref" : "DBSecurityGroup"} ],
          "UserData": {
            "Fn::Base64": { "Fn::Join" : ["", [
            "#!/bin/bash -xe\n",
            "sudo su\n",
            "sudo yum -y update\n",
            "sudo yum -y install mysql-server\n",
            "sudo service mysqld start\n",
            "mysql --user='root' --password='' -e 'CREATE DATABASE ",{"Ref":"DBName"},"'\n",
            "mysql --user='root' --password='' -e \"CREATE USER ",{"Ref":"DBUser"},"@'%' IDENTIFIED BY '",{"Ref":"DBPassword"},"'\"\n",
            "mysql --user='root' --password='' -e \"GRANT ALL ON ",{"Ref":"DBName"},".* to ",{"Ref":"DBUser"},"@'%'\"\n",
            "mysql --user='root' --password='' -e \"FLUSH PRIVILEGES\"\n"
          ]]}},
          "Tags": [
            {
                "Key": "Name",
                "Value": "EC2-mysql"
            }
          ]
      }
    }
  
    },
  
    "Outputs" : {
      "URL" : {
        "Description" : "The URL of the website",
        "Value" :  { "Fn::Join" : [ "", [ "http://", { "Fn::GetAtt" : [ "ElasticLB", "DNSName" ]}]]}
      }
    }
  }

    template["Parameters"]["InstanceType"]["Default"] = request.form["instance"]
    template["Parameters"]["KeyName"]["Default"] = request.form["keyvalue"]
    template["Parameters"]["SSHLocation"]["Default"] = request.form["sshloca"]
    template["Parameters"]["DBName"]["Default"] = request.form["dbname"]
    template["Parameters"]["DBUser"]["Default"] = request.form["dbuser"]
    template["Parameters"]["DBPassword"]["Default"] = request.form["dbpwd"]
    template["Parameters"]["DBRootPassword"]["Default"] = request.form["dbrootpwd"]

    res = client.create_stack(
        StackName=request.form["stackname"],
        TemplateBody= json.dumps(template),
    )
    print(res)
    return res

    
    

app.run()