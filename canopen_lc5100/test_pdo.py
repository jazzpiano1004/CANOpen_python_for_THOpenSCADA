import time
import canopen


        
def canopen_test_pdo(user_os):
    """ 
    	canopen testing : read and write the data using PDO
    	tested device : beckhoff remote I/O LC5100
    """
    print("test PDO")
    # Start with creating a network representing one CAN bus
    net = canopen.Network()
	
    # Connect to the CAN bus
    # Arguments are passed to python-can's can.interface.Bus() constructor
    # (see https://python-can.readthedocs.io/en/latest/bus.html).
    # connection is depended on your OS
    if user_os == "linux":
    	net.connect(bustype='socketcan', channel='can0')
    	print("connect via \'socketcan\' to can0")
    else:
    	net.connect(bustype='usb2can', channel='69E696BD', bitrate=125000)
    	print("connect via \'usb2can\' to channel 69E696BD, bitrate=125000")

    # Add some nodes with corresponding Object Dictionaries
    node_lc5100 = canopen.RemoteNode(node_id=1, object_dictionary='LC5100.eds')
    net.add_node(node_lc5100)
	
    # Set to pre-operational mode
    node_lc5100.nmt.send_command(0x80)
    time.sleep(5)
    
    # Config PDO of node device
    print("Config PDO device")
    node_lc5100.rpdo.read()
    node_lc5100.tpdo.read()
    print("tpdo map (before):\t{}".format(node_lc5100.tpdo[1].map))
    print("tpdo enabled (before):\t{}".format(node_lc5100.tpdo[1].enabled))
    #node_lc5100.rpdo[1].add_variable(0x6200, 1, 8)
    print("tpdo map (after):\t{}".format(node_lc5100.tpdo[1].map))
    print("tpdo enabled (after):\t{}".format(node_lc5100.tpdo[1].enabled))
    
    node_lc5100.tpdo[1].event_timer = 3000
    node_lc5100.tpdo[1].enabled = True
    node_lc5100.tpdo.save()
    node_lc5100.rpdo.save()
    
    # Set to operational mode (Run mode)
    node_lc5100.nmt.send_command(0x01)
    time.sleep(3)
    
    # Test sending PDO to set output of Remote I/O LC5100
    print("Test sending PDO to set output of Remote I/O LC5100")
    try:
        write_data = 0
        while True:
            write_data += 1
            if write_data > 0xFF:
                write_data = 0
            print("Write output value = {}".format(write_data))
            node_lc5100.rpdo[1][0x6200].raw = write_data
            #node_lc5100.rpdo[1].raw = write_data
            node_lc5100.rpdo[1].transmit()
            time.sleep(0.5)
        
    except KeyboardInterrupt:
        print("Exit from sending PDO to LC5100")
	
    # Test reading PDO to read input of Remote I/O LC5100
    print("Test reading PDO to read input of Remote I/O LC5100")
    try:
        while True:
            timestamp = node_lc5100.tpdo[1].wait_for_reception()
            read_value = node_lc5100.tpdo[1][0x6000].raw
            print("Read input value = {}, t={}".format(read_value, timestamp))
        
    except KeyboardInterrupt:
        print("Exit from reading PDO to LC5100")
		
        
if __name__ == '__main__':
    user_os = input("Choose OS of your machine, linux or win (default). : ")
    canopen_test_pdo(user_os)
