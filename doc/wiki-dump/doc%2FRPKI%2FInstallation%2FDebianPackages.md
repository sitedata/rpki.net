# Installation Using Debian Packages on Debian and Ubuntu Systems

Precompiled binary packages for Ubuntu 12.04 LTS ("Precise Pangolin") and
Debian 7 ("Wheezy") are available from download.rpki.net using the Debian
Advanced Package Tools (APT). To use these, you need to configure APT on your
machine to know about our APT repository, but once you've done this you should
be able to install and update these packages like any other precompiled
package.

## Initial APT Setup

You should only need to perform these steps once for any particular machine.

  * Add the GPG public key for this repository (optional, but APT will whine unless you do this): 
    
        wget -q -O - https://download.rpki.net/APT/apt-gpg-key.asc | sudo apt-key add -
    

  * Configure APT to use this repository (for Ubuntu Trusty systems): 
    
        sudo wget -q -O /etc/apt/sources.list.d/rpki.list https://download.rpki.net/APT/rpki.trusty.list
    

  * Configure APT to use this repository (for Ubuntu Precise systems): 
    
        sudo wget -q -O /etc/apt/sources.list.d/rpki.list https://download.rpki.net/APT/rpki.precise.list
    

  * Configure APT to use this repository (for Debian Wheezy systems): 
    
        sudo wget -q -O /etc/apt/sources.list.d/rpki.list https://download.rpki.net/APT/rpki.wheezy.list
    

## Installation Using APT Tools

These instructions assume that you're using apt-get. Other APT tools such as
aptitude should also work.

  * Update available packages: 
    
        sudo apt-get update
    

  * Install the software: 
    
        sudo apt-get install rpki-rp rpki-ca
    

  * Customize the default `rpki.conf` for your environment as necessary. In particular, you want to change `handle` and `rpkid_server_host`. There are [obsessively detailed instructions][1]. 
    
        sudo emacs /etc/rpki.conf
    

> Again, you want to change `handle` and `rpkid_server_host` at the minimum.

  * If you changed anything in `rpki.conf`, you should restart the RPKI CA service: 
    
        sudo service rpki-ca restart
    

## Upgrading

Once you've performed the steps above you should be able to upgrade to newer
version of the code using the normal APT upgrade process, eg:

    
    
    sudo apt-get update
    sudo apt-get upgrade
    

Or, if you only want to update the RPKI tools:

    
    
    sudo apt-get update
    sudo apt-get upgrade rpki-ca rpki-rp
    

   [1]: #_.wiki.doc.RPKI.CA.Configuration

