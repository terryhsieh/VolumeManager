"""
Utility functions for bootserver to create client images and volumes.
"""

import os
import command
import logging
from shutil import copytree, rmtree

bootServerIp = commands.getoutput("ifconfig").split("\n")[1].split()[1][5:]
templateStor = "/templateVol"
exportRootPath = bootServerIp+":/templateVol"

logger = logging.getLogger('volumemanager')
hdlr = logging.FileHandler('volumemanager.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

deployDictSample = {    'zone_id':'zone001',

                        'host_list':[
                                        {'hostname':'host1',
                                         'ip':'192.168.100.31',
                                         'kernel':'vmlinuz-3.2.0-23-generic',
                                         'ramdisk':'initrd.img-3.2.0-23-generic',
                                         'volume':'vol_openstack',
                                         'read_only':False},

                                        {'hostname':'host2',
                                         'ip':'192.168.100.32',
                                         'kernel':'vmlinuz-3.2.0-23-generic',
                                         'ramdisk':'initrd.img-3.2.0-23-generic',
                                         'volume':'vol_openstack',
                                         'read_only':True},

                                        {'hostname':'host3',
                                         'ip':'192.168.100.33',
                                         'kernel':'vmlinuz-3.2.0-23-generic',
                                         'ramdisk':'initrd.img-3.2.0-23-generic',
                                         'volume':'vol_openstack',
                                         'read_only':True}
                                    ]

		   }


def boot_host(deployDict):
	
	check_current_status(deployDict)
	
	create_volume(deployDict)
	
	append_to_exports_file(deployDict)
	
	call_bgcommander(deployDict)	
			

def check_current_status(deployDict):

	if ( not os.path.isdir(templateStor)):
        	logger.error("The tempate storage folder does not exist!, check if the iSCSI connection to backend storage correctly")
		logger.debug('Input parameter: '+str(deployDict))

        # delete if folder named zone_id exist
        if ( os.path.isdir(templateStor + '/' + deployDict.get('zone_id'))):
                logger.info('The zone id: ' + deployDict.get('zone_id') + ' already existed in the template Storage')
                logger.info('Delete zone id: '+deployDict.get('zone_id'))
                rmtree(templateStor + '/' + deployDict.get('zone_id'))
                logger.info('zone_id: ' +deployDict.get('zone_id')+' was deleted')


def create_volume(deployDict):

	for host in deployDict.get('host_list'):
		if host.get('read_only'): #create one ro volume
			if ( not  os.path.isdir(templateStor + '/' + deployDict.get('zone_id')+'/'+'ro')):
				source_dir = templateStor+'/'+host.get('volume')
               			dest_dir = templateStor+'/'+deployDict.get('zone_id')+'/'+'ro'
                		copytree(source_dir,dest_dir)
                		logger.info('volume '+host.get('volume')+'has already copy to '+dest_dir)
			
		else: #create rw volume for each host
			source_dir = templateStor+'/'+host.get('volume')
			dest_dir = templateStor+'/'+deployDict.get('zone_id') + '/rw/' + host.get('hostname')
			copytree(source_dir,dest_dir)


# The export entry based on zone_id, ex: one zone has one export entry 
def append_to_exports_file(deployDict):

	exports_file = open('/etc/exports','a+r')
	flag_ro = False
	flag_rw = False
    
	for host in deployDict.get('host_list'):
		if (host.get('read_only') == True):
			flag_ro = True
	#		entry = templateStor +'/' + deployDict.get('zone_id') +'\t' + '*(ro,async,no_root_squash,no_subtree_check)'+'\n'
		if (host.get('read_only') == False):
			flag_rw = True
	#		entry = templateStor +'/' + deployDict.get('zone_id') +'\t' + '*(rw,async,no_root_squash,no_subtree_check)'+'\n'

	if (flag_ro == True):
		entry = templateStor + '/' + deployDict.get('zone_id') + '/ro' + '\t' + '*(ro,async,no_root_squash,no_subtree_check)' + '\n'
		exports_file.write(entry)
	if (flag_rw == True):
		entry = templateStor + '/' + deployDict.get('zone_id') + '/rw' + '\t' + '*(rw,async,no_root_squash,no_subtree_check)' + '\n'
                exports_file.write(entry)

	exports_file.close()
	os.system('exportfs -rv')


def call_bgcommander(deployDict):

	nfs_path = templateStor+'/'+deployDict.get('zone_id')
	for host in deployDict.get('host_list'):
		if (host.get('read_only') == True):
			command = './bgcommander ' + host.get('ip')+' '+exportRootPath+'/'+deployDict.get('zone_id')+'/ro'
			print('ro: '+command)
			#os.system(command)
		else:
			command = './bgcommander ' + host.get('ip')+' '+exportRootPath+'/'+deployDict.get('zone_id')+'/rw/'+host.get('hostname')
			print('rw: '+command)
			#os.system(command)	

def reboot(hostname, addr):
	return True


def shutdown(hostname, addr):
	return True


def listImages():
	pass


def main():
	boot_host(deployDictSample)


if __name__ == '__main__':
	main()

