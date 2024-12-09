# BiliBili_mall_autosearch
This is a script for BiliBili marketshop format match searching./魔力赏抓取器

# 依赖与设置指南 / Dependencies and Setup Guide

## 依赖 / Dependencies
这个脚本需要的依赖有：
- `tkinter`
- `selenium`

同时，你的设备需要装有Chrome以及相应版本的Chrome Driver（你需要记住Chrome Driver放置的位置）。

This script requires the following dependencies:
- `tkinter`
- `selenium`

Also, your device must have Chrome and the corresponding version of Chrome Driver installed (remember where you placed the Chrome Driver).

## 设置步骤 / Setup Steps
1. **配置Chrome Driver路径 / Configure Chrome Driver Path**
   先阅读并遵循Coconut_Cake在[此文章](https://blog.csdn.net/Asimoedeus/article/details/134785699)中提出的header抓取方法。
   在`b_sj_search_ver2.0.py`的第23行将headers占位部分全部替换为你自己的header；之后，转到第215行，将你的Chrome Driver的完整路径填入。

   First, read and follow the header fetching method proposed by Coconut_Cake in [this article](https://blog.csdn.net/Asimoedeus/article/details/134785699).
   In `b_sj_search_ver2.0.py`, replace all placeholder parts of headers at line 23 with your own headers; then, go to line 215 and fill in the full path of your Chrome Driver.

2. **运行脚本 / Run the Script**
   在完成上述设置后，在cmd中cd到clone文件夹的主目录运行`python b_sj_search_ver2.0.py`，然后你会发现一些有趣的事情发生。

   After completing the above settings, cd into the main directory of the clone folder in cmd and run `python b_sj_search_ver2.0.py`, then you will discover some interesting things happening.


Whole script is created by 飯野龍馬
