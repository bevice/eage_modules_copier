# Eagle cad module copier

How to use:
1. Create schematic with modules (e.g.: MODULE1, MODULE2, MODULE3 etc)
2. Create the board and route MODULE1 layout
4. Run:
````bash   
    python module_copy.py --in board.brd --out copied.brd \
    --ref-design MODULE1 \
    --ref-element R1 \
    --modify-module MODULE2 MODULE3 MODULE4
````    
Where: 

* *--in* - input file
* *--out* - output file
* *--ref-design* - module whose design will be used as the reference
* *--ref-element* - element name whose place will be used as the reference
* *--modify-module* - names of modules whose layouts will be modified

![Prepared board](https://github.com/bevice/eage_modules_copier/raw/master/prepare.png)

The script converts to:

![Result board](https://github.com/bevice/eage_modules_copier/raw/master/result.png)

