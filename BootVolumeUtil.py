"""
Utility functions for bootserver to create client images and volumes.
"""

import os
from shutil import copytree, rmtree

StorageMountPoint="/templateVol"
ExportPath="192.168.100.10:/nfsroot_test"


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
			call_bgcommander()
		else:
			print('copy...')
			source_dir = StorageMountPoint+'/'+deployDict.get('volume')
                        dest_dir = StorageMountPoint+'/'+deployDict.get('zone_id')
                        copytree(source_dir,dest_dir)
			
			modify_exports_file(deployDict.get('zone_id'))	
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
	file = open('/etc/exports','a+r')
	entry = StorageMountPoint +'/' + zone_id +'\t' + '*(rw,async,no_root_squash)'+'\n'
	if (file.read().find(zone_id)):
		print(zone_id + 'entry already existed in the exports file')
	else:
		file.write(entry)
	file.close()
	
	os.system('exportfs -rv')

def call_bgcommander(client_ip, nfs_path, volume_readonly):
	if (volume_readyonly == True):
		#os.system('bgcommander '+ client_ip +' '+nfs_path + ' ' + 'ro')
		print('bgcommander '+ client_ip +' '+nfs_path + ' ' + 'ro')
	else:
		#os.system('bgcommander '+ client_ip + ' '+ nfs_path + ' ' + 'rw')
		print('bgcommander '+ client_ip + ' '+ nfs_path + ' ' + 'rw')

def main():
#	boot_up_by_images(deployDictSample)
	volume_name = StorageMountPoint+'/'+deployDictSample.get('zone_id')
	modify_exports_file(volume_name)
if __name__ == '__main__':
	main()

