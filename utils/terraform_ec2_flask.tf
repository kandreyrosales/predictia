provider "aws" {
  region = "us-east-1"  # Change to your desired region
}

resource "aws_instance" "flask_ec2" {
  ami                    = "ami-0c7217cdde317cfec"  # Replace with your desired AMI ID
  instance_type          = "t2.micro"            # Change instance type as needed
  key_name               = "ec2-user"       # Change to your SSH key pair name
  associate_public_ip_address = true            # Assign a public IP address
  
  provisioner "remote-exec" {
    inline = [
      # Install required packages
      "sudo apt-get update -y",
      "sudo apt-get install -y python3 git",
      "sudo apt-get install -y python3-pip",
      "sudo apt-get install -y python3-venv",  # Install python3-venv package for virtual environments

      # Clone Flask application from GitHub
      "git clone https://github.com/kandreyrosales/predictia-xaldigital.git /home/ubuntu/flask_app",
      
      # Create and activate virtual environment
      "cd /home/ubuntu/flask_app",
      "python3 -m venv venv",
      "source venv/bin/activate",
      
      # Install dependencies
      "pip install -r requirements.txt",

      # Install Gunicorn
      "pip install gunicorn",

      "sudo ufw allow 5000",

      # Create a systemd service for Gunicorn
      "cat <<EOF | sudo tee /etc/systemd/system/flask_app.service",
      "[Unit]",
      "Description=Gunicorn instance to serve Flask application",
      "After=network.target",

      "[Service]",
      "User=ubuntu",
      "Group=ubuntu",
      "WorkingDirectory=/home/ubuntu/flask_app",
      "Environment=\"PATH=/home/ubuntu/flask_app/venv/bin\"",
      "ExecStart=/home/ubuntu/.local/bin/gunicorn -w 1 -b 0.0.0.0:5000 app:app",
      "Restart=always",

      "[Install]",
      "WantedBy=multi-user.target",
      "EOF",

      # Start and enable the Gunicorn service
      "sudo systemctl daemon-reload",
      "sudo systemctl start flask_app",
      "sudo systemctl enable flask_app",
    ]
    
    connection {
      type        = "ssh"
      user        = "ubuntu"  # SSH username for Amazon Linux, CentOS, or Red Hat AMIs
      private_key = file("/Users/kevinrosalesferreira/Downloads/ec2-user.pem")  # Replace with the path to your SSH private key file
      host        = self.public_ip
    }
  }

  tags = {
    Name = "PredictIA-Flask-Ubuntu"
  }

  vpc_security_group_ids = [aws_security_group.flask_sg.id]
}

resource "aws_security_group" "flask_sg" {
  name        = "flask_sg"
  description = "Security group for Flask EC2 instance"

  // Ingress rule to allow HTTP traffic from anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  // Allow traffic from any IPv4 address
  }
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"   // Allow all protocols
    cidr_blocks     = ["0.0.0.0/0"]  // Allow traffic to any IPv4 address
  }
}

output "public_ip" {
  value = aws_instance.flask_ec2.public_ip
}
