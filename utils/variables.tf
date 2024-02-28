# variables.tfvars

variable "region_aws" {
 type        = string
 description = "AWS Region"
 default     = "us-east-1"
}

variable "aws_account_number" {
 type        = string
 description = "AWS Account Number"
 default     = "SDASDAD"
}

variable "cognito_pool_name" {
 type        = string
 description = "AWS Congito Pool ID"
 default     = "predictiauserpool"
}


variable "instance_type" {
 type        = string
 description = "AWS Instance Type"
 default     = "t2.micro"
}

variable "ami" {
 type        = string
 description = "Linux Image from AWS"
 default     = "ami-0c7217cdde317cfec"
}

variable "bucket_name" {
 type        = string
 description = "Bucket name for project data (model files, csv files, etc.)"
 default     = "predictiaxaldigital"
}

variable "accessKeyId" {
 type        = string
 description = "accessKeyId AWS"
 default     = "ASDASDASDASDASD"
}

variable "secretAccessKey" {
 type        = string
 description = "secretAccessKey AWS"
 default     = "zSDSADASDASDASDAS"
}

variable "ssh_key_pair_name" {
 type        = string
 description = "Your SSH key pair name got from EC2"
 default     = "ec2-user"
}

variable "github_repo" {
 type        = string
 description = "Repo with the Flask code. Change remote exec to use private repo"
 default     = "https://github.com/kandreyrosales/predictia.git"
}

variable "private_key_ec2_path" {
 type        = string
 description = "PEM file path in your computer"
 default     = "/Users/kevinrosalesferreira/Downloads/ec2-user.pem"
}

variable "lambda_layer_pandas" {
 type        = string
 description = "Layer for Lambdas Python"
 default     = "arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p312-pandas:2"
}