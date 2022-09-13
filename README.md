# SPEM: Self-adaptive Pooling Enhanced Attention Module for Image Recognition
[![996.ICU](https://img.shields.io/badge/link-996.icu-red.svg)](https://996.icu) 
![GitHub](https://img.shields.io/github/license/gbup-group/DIANet.svg)
![GitHub](https://img.shields.io/badge/Qrange%20-group-orange)

This repository is the implementation of "SPEM: Self-adaptive Pooling Enhanced Attention Module for Image Recognition" [[paper]](https://arxiv.org/abs/?)  on CIFAR-100 and CIFAR-10 datasets. Our paper has been accepted for presentation at ???. You can also check with the [??? proceeding version](???).

## Introduction

SPEM is a self-attention module. We empirically find and verify a phenomenon that the simple linear combination of global max-pooling and global min-pooling can produce pooling strategies that match or exceed the performance of global average pooling. Based on this empirical observation, we propose a simple-yet-effective self-attention module SPEM, which adopts a self-adaptive pooling strategy based on global max-pooling, global min-pooling and a lightweight module for producing the attention map. 

<p align="center">
  <img src="https://github.com/Qrange-group/SPEM/blob/main/images/arch.png" width="600" height="300">
</p>

## Requirement
Python and [PyTorch](http://pytorch.org/).
  ```
  pip install -r requirements.txt
  ```
## Usage
  ```
CUDA_VISIBLE_DEVICES=0 python run.py --dataset cifar100 --block-name bottleneck --depth 164 --epochs 164 --schedule 81 122 --gamma 0.1 --wd 1e-4
  ```

## Results
|                 |  Dataset  | original |  SPEM  |
|:---------------:|:------:|:--------:|:------:|
|    ResNet164    |CIFAR10 |   93.39  |  94.80 |
|    ResNet164    |CIFAR100|   74.30  |  76.31 |



## Citing SPEM

```
???
```

## Acknowledgments
Many thanks to [bearpaw](https://github.com/bearpaw) for his simple and clean [Pytorch framework](https://github.com/bearpaw/pytorch-classification) for image classification task.
