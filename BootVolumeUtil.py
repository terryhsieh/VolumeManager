"""
Utility functions for bootserver to create client images and volumes.
"""

import os
from shutil import copytree, rmtree

StorageMountPoint="/templateVol"
ExportPath="192.168.100.10:/nfsroot_test"
my_ip = '192.168.100.101'


#check if mount point exist

deployDictSample = {	'zone_id':'zone001',
			'hostname':['host1','host2'],
			'addr':['192.168.100.30','192.168.100.31'],
			'kernel':'vmlinuz-3.2.0-23-generic',
			'ramdisk':'initrd.img-3.2.0-23-generic',
			'volume':'vol_openstack',
			'volume_readonly':True}

if ( not os.path.ismount(StorageMountPoint)):
	print("The mount point does not exist!, mount it~")
	cmd=" sudo mount -t nfs " + ExportPath + " " + StorageMountPoint
	os.system(cmd)

def boot_up_by_images(deployDict):
	print(deployDict)
	if deployDict.get("volume_readonly") == True:
		print('volume_readonly is True')
		if ( os.path.isdir(StorageMountPoint+'/'+deployDict.get('zone_id'))):
			print('zone already existed, delete it.')
			rmtree(StorageMountPoint+'/'+deployDict.get('zone_id'))
			
			source_dir = StorageMountPoint+'/'+deployDict.get('volume')
			dest_dir = StorageMountPoint+'/'+deployDict.get('zone_id')
			copytree(source_dir,dest_dir)
			
			modify_exports_file(deployDict.get('zone_id'))
			call_bgcommander(deployDict)
		else:
			print('copy...')
			source_dir = StorageMountPoint+'/'+deployDict.get('volume')
                        dest_dir = StorageMountPoint+'/'+deployDict.get('zone_id')
                        copytree(source_dir,dest_dir)
			
			modify_exports_file(deployDict.get('zone_id'))	
			call_bgcommander(deployDict)
	else:
		print('volume_readonly is False')
		if ( os.path.isdir(StorageMountPoint+'/'+deployDict.get('zone_id'))):
			print('zone already existed, delete it.')
			rmtree(StorageMountPoint+'/'+deployDict.get('zone_id'))
			
			source_dir = StorageMountPoint+'/'+deployDict.get('volume')
			for node in deployDict.get('hostname'):
				dest_dir = StorageMountPoint+'/'+deployDict.get('zone_id') + '/nodes/' + node
				copytree(source_dir, dest_dir)

				modify_exports_file(deployDict.get('zone_id'))
		else:
			print('copy.....')
			source_dir = StorageMountPoint+'/'+deployDict.get('volume')
                        for node in deployDict.get('hostname'):
                                dest_dir = StorageMountPoint+'/'+deployDict.get('zone_id') + '/nodes/' + node
                                copytree(source_dir, dest_dir)
				modify_exports_file(deployDict.get('zone_id'))
def reboot(hostname, addr):
	return True

def shutdown(hostname, addr):
	return True

def listImages():
	pass

# The export entry based on zone_id, ex: one zone has one export entry 
def modify_exports_file(zone_id):
	print(zone_id)
	myfile = open('/etc/exports','a+r')
	entry = StorageMountPoint +'/' + zone_id +'\t' + '*(rw,async,no_root_squash,no_subtree_check)'+'\n'
	if (myfile.read().find(zone_id) > 0):
		print(zone_id + ' entry already existed in the exports file')
	else:
		myfile.write(entry)
	myfile.close()
	
	os.system('exportfs -rv')

def call_bgcommander(deployDict):
	if (deployDict.get('volume_readyonly') == True):
		nfs_path = StorageMountPoint+'/'+deployDict.get('zone_id')
		for t_addr in deployDict.get('addr'):
			command = 'bgcommander ' + ip + ' ' + nfs_path + 'ro'
			print(command)
#			os.system(command)
	else:
		nfs_path = StorageMountPoint+'/'+deployDict.get('zone_id')
		for i in range(len(deployDict.get('hostname'))):
			command = 'bgcommander '+ deployDict.get('addr')[i] + ' ' +nfs_path+'/'+deployDict.get('hostname')[i] + 'rw'
			print(command)
#			os.system(command) 	

def main():
	boot_up_by_images(deployDictSample)
#	zone_id='zone001'
#	myfile = open('/etc/exports','a+r')
#	print(myfile.read().find(zone_id))
#	if (myfile.read().find(zone_id)):
#                print(zone_id + ' entry already existed in the exports file')
if __name__ == '__main__':
	main()

