#!/bin/bash
my_dir=$(cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd)


out="$( readlink -f "$my_dir/../")/out/tmp"
bin="$( readlink -f "$my_dir/../bin" )"
res="$( readlink -f "$my_dir/../res" )"
src="$( readlink -f "$my_dir/../src" )"
source "$bin/env.sh"

mkdir -p "$out" > /dev/null 2>&1

python3 "$src/plot_laser.py" "$res/laser/405nm.csv"   "$out/laser-405nm.pdf"
python3 "$src/plot_laser.py" "$res/laser/445nm.csv"   "$out/laser-445nm.pdf"
python3 "$src/plot_laser.py" "$res/laser/532nm.csv"   "$out/laser-532nm.pdf"
python3 "$src/plot_laser.py" "$res/laser/635nm_2.csv" "$out/laser-635nm.pdf"
python3 "$src/plot_laser.py" "$res/laser/405nm.csv" \
	                     "$res/laser/445nm.csv" \
	                     "$res/laser/532nm.csv" \
	                     "$res/laser/635nm_2.csv" "$out/lasers.pdf"

python3 "$src/plot_led.py"   "$res/led/yealink/green.csv"  "$out/led-yealink-green.pdf" --colors green
python3 "$src/plot_led.py"   "$res/led/yealink/red_1.csv"  "$out/led-yealink-red.pdf" --colors red
python3 "$src/plot_led.py"   "$res/led/yealink/green.csv" \
	                     "$res/led/yealink/red_1.csv"  "$out/leds-yealink.pdf" --colors green red

python3 "$src/plot_led.py"   "$res/led/selection/red.csv" \
			     "$res/led/selection/green-yellow.csv" \
	                     "$res/led/selection/blue.csv" \
	                     "$res/led/selection/orange.csv" \
	                     "$res/led/selection/white.csv" \
	                     "$res/led/selection/green.csv" \
	                     "$res/led/selection/yellow.csv"  "$out/leds-selection.pdf" \
	                     --colors red y blue orange black green \#F1F33F

python3 "$src/plot_opticalpower.py" \
                             "$res/laser/characteristic_engraving.txt" \
                             "$res/laser/characteristic_green.txt" "$out/laser-characteristic.pdf" \
	                     --colors \#1f77b4 \#2CA02C

python3 "$src/plot_freqresponse.py" \
                             "$res/APD440A2/APD440A2-frequency.csv" \
                              "$out/APD440A2-frequency.pdf" \
                             #--colors black

python3 "$src/plot_responsitivity.py" \
                             "$res/APD440A2/APD440A2-responsivity.csv" \
                             "$out/APD440A2-responsivity.pdf" \
                             --colors blue green \#F1F33F orange red

python3 "$src/plot_bandwidth.py" \
                             "$res/led/selection/bandwidth/yellow.csv" \
                             "$res/led/selection/bandwidth/green-yellow.csv" \
                             "$res/led/selection/bandwidth/green.csv" "$out/leds-selection-bandwidth-1.pdf" \
	                     --colors \#F1F33F y green

python3 "$src/plot_bandwidth.py" \
                             "$res/led/selection/bandwidth/orange.csv" \
                             "$res/led/selection/bandwidth/red.csv" \
                             "$res/led/selection/bandwidth/blue.csv" \
                             "$res/led/selection/bandwidth/white.csv" "$out/leds-selection-bandwidth-2.pdf" \
	                     --colors orange red blue black

python3 "$src/plot_bandwidth.py" \
                             "$res/led/yealink/bandwidth/green.csv" \
                             "$res/led/yealink/bandwidth/red-1.csv" \
                             "$res/led/yealink/bandwidth/red-2.csv"   "$out/leds-yealink-bandwidth.pdf" \
	                     --colors \#2CA02C red \#FF800E 



ln -s "$out/leds-yealink.pdf" "$out/../figure2-top.pdf"
ln -s "$out/lasers.pdf" "$out/../figure2-bottom.pdf"

ln -s "$out/leds-selection.pdf" "$out/../figure6.pdf"
ln -s "$out/laser-characteristic.pdf" "$out/../figure7.pdf"
ln -s "$out/APD440A2-responsivity.pdf" "$out/../figure8.pdf"

ln -s "$out/leds-selection-bandwidth-1.pdf" "$out/../figure10a.pdf"
ln -s "$out/leds-selection-bandwidth-2.pdf" "$out/../figure10b.pdf"
ln -s "$out/leds-yealink-bandwidth.pdf" "$out/../figure10c.pdf"

ln -s "$out/APD440A2-frequency.pdf" "$out/../figure12.pdf"

