#!/bin/bash

cd ../Shell
while true;
do
	case $(python3 ./flash.py -q) in
	maskrom)
		echo
		echo Found One Maskrom Device
		echo
		break
		;;
	loader)
		echo
		echo Found One Loader Device
		echo
		break
		;;
	*)
		echo -n "."
		;;
	esac
sleep 1
done

echo "Please Press Any Key to Continue: "
read key
python3 ./flash.py --dual all
