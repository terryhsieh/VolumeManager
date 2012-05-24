"""
Utility functions for bootserver to create client images and volumes.
"""

import os
from shutil import copytree, rmtree

bootServerIp = '192.168.100.101'

templateStor = "/templateVol"
exportRootPath = bootServerIp+":/templateVol"

deployDictSample = {	'zone_id':'zone001',
			'hostname':['host1','host2'],
			'addr':['192.168.100.30','192.168.100.31'],
			'kernel':'vmlinuz-3.2.0-23-generic',
			'ramdisk':'initrd.img-3.2.0-23-generic',
			'volume':'vol_openstack',
			'volume_readonly':False}

# check if /templateStor exist 
if ( not os.path.isdir(templateStor)):
	print("The tempate storage folder does not exist!, check if the iSCSI connection to backend storage correctly")

def boot_up_by_images(deployDict):
	
	if ( os.path.isdir(templateStor + '/' + deployDict.get('zone_id'))):
		print('The zone id: ' + deployDict.get('zone_id') + ' already existed in the template Storage, delete it.')
		rmtree(templateStor + '/' + deployDict.get('zone_id'))
	
	if deployDict.get("volume_readonly") == True:
		print('volume_readonly is True')
			
		source_dir = templateStor+'/'+deployDict.get('volume')
		dest_dir = templateStor+'/'+deployDict.get('zone_id')
		copytree(source_dir,dest_dir)
		
		modify_exports_file(deployDict)
		call_bgcommander(deployDict)

	else:
		print('volume_readonly is False')

		source_dir = templateStor+'/'+deployDict.get('volume')
		for node in deployDict.get('hostname'):
			dest_dir = templateStor+'/'+deployDict.get('zone_id') + '/nodes/' + node
			copytree(source_dir, dest_dir)
			modify_exports_file(deployDict)
		call_bgcommander(deployDict)

def reboot(hostname, addr):
	return True

def shutdown(hostname, addr):
	return True

def listImages():
	pass

# The export entry based on zone_id, ex: one zone has one export entry 
def modify_exports_file(deployDict):
	myfile = open('/etc/exports','a+r')
	if (deployDict.get('volume_readonly') == True):
		entry = templateStor +'/' + deployDict.get('zone_id') +'\t' + '*(ro,async,no_root_squash,no_subtree_check)'+'\n'
	else:
		entry = templateStor +'/' + deployDict.get('zone_id') +'\t' + '*(rw,async,no_root_squash,no_subtree_check)'+'\n'


	if (myfile.read().find(deployDict.get('zone_id')) > 0):
		print(' The zone id: ' + deployDict.get('zone_id') + ' already existed in the exports file')
	else:
		myfile.write(entry)

	myfile.close()
	os.system('exportfs -rv')

def call_bgcommander(deployDict):
	if (deployDict.get('volume_readonly') == True):
		nfs_path = templateStor+'/'+deployDict.get('zone_id')
		for t_addr in deployDict.get('addr'):
			command = './bgcommander ' + ip + ' ' + nfs_path + 'ro'
			print(command)
#			os.system(command)
	else:
		nfs_path = templateStor+'/'+deployDict.get('zone_id')
		for i in range(len(deployDict.get('hostname'))):
			command = './bgcommander '+ deployDict.get('addr')[i] + ' ' +exportRootPath+'/'+deployDict.get('zone_id')+'/nodes/'+deployDict.get('hostname')[i] + ',rw'
			print(command)
#			os.system(command) 	

def main():
	boot_up_by_images(deployDictSample)

if __name__ == '__main__':
	main()

