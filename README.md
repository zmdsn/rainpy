<h1 align="center">
<img src="https://raw.githubusercontent.com/zmdsn/rainpy/refs/heads/main/doc/rainpylogo.jpg" width="300">
</h1><br>

![](https://img.shields.io/badge/rainpy-base-blue?logo=N&labelColor=white)
![](https://img.shields.io/badge/License-BSD-blue?logo=N&labelColor=white)

# rainpy

For the Scientific Research to test problems.

## easy to read or save file 

### easy to read a file

> rainpy.read(file_path, *args, *kwargs)

### easy to write a file

> rainpy.save(file_path, *args, *kwargs)
or
> rainpy.write(file_path, *args, *kwargs)


## easy to start a project

> rainpy -n example -a zmdsn -e zmdsn@126.com

## easy to run a python function with file

> def func(data):
>     data['base'] = "rainpy base"
>     return data

> rainpy --run func.py --file ./test.json --save ./result.json

or

> @rainpy(from="./test.json", to="./result.json")
> def func(data):
>     data['base'] = "rainpy base"
>     return data
