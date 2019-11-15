# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "lasp/ubuntu16.04"
  config.ssh.forward_x11 = true
  config.vm.network "forwarded_port", guest: 8880, host: 2200
  config.vm.define "ip2019" do |vm|
  end
  ## CPU & RAM
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--cpuexecutioncap", "100"]
    vb.memory = 4192
    vb.cpus = 2
  end
  config.vm.provision "shell", inline: <<-SHELL
     # Start in /vagrant instead of /home/vagrant
     if ! grep -Fxq "cd /vagrant" /home/vagrant/.bashrc
     then
      echo "cd /vagrant" >> /home/vagrant/.bashrc
     fi
  SHELL
  config.vm.synced_folder ".", "/vagrant"
  config.vm.provision "shell", path: "scripts/root-bootstrap.sh"
  config.vm.provision "shell", privileged: false, path: "scripts/user-bootstrap.sh"

end
