#!/isan/bin/ python
from cisco import transfer
from cli import *
import re
import sys

build_version = sys.argv[1]
n9k_release_version = "7.0.3.I2.0"
image_dir_src = "//auto/tftpboot/images"
n9k_system_image = "n9000-dk9.%s.%s.bin" % (n9k_release_version, build_version)
image_dir_dst = "bootflash:"
required_space = 250000
protocol = "scp" 
ftp_username = "undhiyu"
ftp_password = sys.argv[2]
hostname = "22.25.25.54"
vrf = "management"
system_timeout = 3100 
system_image_src = "%s/%s" % (image_dir_src, n9k_system_image)

def run_cli (cmd):
    print "CLI : %s" % cmd
    r=cli(cmd)
    return r
        
def verify_freespace (): 
    out=run_cli("dir bootflash: | grep free")
    match = re.search("^([0-9]+)\s+bytes\s+free$", out)
    if match:
        freespace=int(match.group(1))/1024
    else:
        print "ERR: Unable to get free space details"
        exit(1)
    print "INFO: free space is %s kB"  % freespace

    if required_space > freespace:
        print "ERR : Not enough space to copy the system image, aborting!"
        exit(1)
    return
    
# transfers file, return True on success; on error exits unless 'fatal' is False in which case we return False
def doCopy(protocol = "", host = "", source = "", dest = "", vrf = "management", login_timeout=10, user = "", password = "", fatal=True):
    try:
        transfer.transfer(protocol, host, source, dest, vrf, login_timeout, user, password)
    except Exception as inst:
        print "WARN: Copy Failed: %s" % inst
        if fatal:
            exit(1)
        return
    return
    
# get system image file from server
def get_system_image ():
    print "Transfer protocol is %s" % protocol
    print "Remote Server is %s" % hostname
    print "Source Image Path is %s" % system_image_src
    print "Username is %s" % ftp_username
#    print "Password is %s" % ftp_password
    doCopy (protocol, hostname, system_image_src, n9k_system_image, vrf, system_timeout, ftp_username, ftp_password)  
    print "Completed Copy of System Image"
    
# install (make persistent) images and config 
def install_it (): 
    print "INFO: Setting the boot variables"
    try:
        cmd = "config terminal ; no boot nxos"
        run_cli (cmd)
        cmd = "config terminal ; boot nxos %s%s" % (image_dir_dst, n9k_system_image)
        run_cli (cmd)
        cmd = "copy running-config startup-config"
        run_cli (cmd)
    except:
        print "ERR : setting bootvars or copy run start failed!"
        sys.stdout.flush()
        exit(1)
    print "INFO: Configuration successful"
    print "DONE."
    return

verify_freespace()
get_system_image()
install_it()
