# Running rpkid or pubd on a different server

The default configuration runs rpkid, pubd (if enabled) and the back end code
all on the same server. For many purposes, this is fine, but in some cases you
might want to split these functions up among different servers.

As noted briefly above, there are two separate sets of rpki.conf options which
control the necessary behavior: the `run_*` options and the `start_*` options.
The latter are usually tied to the former, but you can set them separately,
and they control slightly different things: the `run_*` options control
whether the back end code attempts to manage the servers in question, while
the `start_*` flags control whether the startup scripts should start the
servers in question.

Here's a guideline to how to set up the servers on different machines. For
purposes of this description we'll assume that you're running both rpkid and
pubd, and that you want rpkid and pubd each on their own server, separate from
the back end code. We'll call these servers rpkid.example.org,
pubd.example.org, and backend.example.org.

Most of the configuration is the same as in the normal case, but there are a
few extra steps. The following supplements but does not replace the normal
instructions.

**WARNING**: These setup directions have not (yet) been tested extensively. 

  * Create rpki.conf as usual on backend.example.org, but pay particular attention to the settings of `rpkid_server_host`, `irbe_server_host`, and `pubd_server_host`: these should name rpkid.example.org, backend.example.org, and pubd.example.org, respectively. 
  * This example assumes that you're running pubd, so make sure that both `run_rpkid` and `run_pubd` are enabled in rpki.conf. 
  * Copy the rpki.conf to the other machines, and customize each copy to that machine's role: 
    * `start_rpkid` should be enabled on rpkid.example.org and disabled on the others. 
    * `start_pubd` should be enabled on pubd.example.org and disabled on the others. 
    * `start_irdbd` should be enabled on backend.example.org and disabled on the others. 
  * Make sure that you set up SQL databases on all three servers; the `rpki-sql-setup` script should do the right thing in each case based on the setting of the `start_*` options. 
  * Run "rpkic initialize" on the back end host. This will create the BPKI and write out all of the necessary keys and certificates. 
  * "rpkic initialize" should have created the BPKI files (.cer, .key, and .crl files for the several servers). Copy the .cer and .crl files to the pubd and rpkid hosts, along with the appropriate private key: rpkid.example.org should get a copy of the rpkid.key file but not the pubd.key file, while pubd.example.org should get a copy of the pubd.key file but not the rpkid.key file. 
  * Run `rpki-start-servers` on each of the three hosts when it's time to start the servers. 
  * Do the usual setup dance, but keep in mind that the the back end controlling all of these servers lives on backend.example.org, so that's where you issue the rpkic or GUI commands to manage them. rpkic and the GUI both know how to talk to rpkid and pubd over the network, so managing them remotely is fine. 

