# SPENet: Self-adaptive Pooling Enhance for Self-attention Mechanism on Image Recognition
[![996.ICU](https://img.shields.io/badge/link-996.icu-red.svg)](https://996.icu) 
![GitHub](https://img.shields.io/github/license/gbup-group/DIANet.svg)
![GitHub](https://img.shields.io/badge/gbup-%E7%A8%B3%E4%BD%8F-blue.svg)

This repository is the implementation of "SPENet: Self-adaptive Pooling Enhance for Self-attention Mechanism on Image Recognition" [[paper]](https://arxiv.org/abs/?)  on CIFAR-100 and CIFAR-10 datasets. Our paper has been accepted for presentation at ???. You can also check with the [??? proceeding version](???).

## Introduction

SPENet is an slef-attention module. We empirically find and verify a phenomenon that the simple linear combination of global max-pooling and global min-pooling can produce pooling strategies that match or exceed the performance of global average pooling. Based on this empirical observation, we propose a simple-yet-effective self-attention module SPENet, which adopts a self-adaptive pooling strategy based on global max-pooling and global min-pooling and a lightweight module for producing the attention map. 

<p align="center">
  <img src="https://github.com/gbup-group/IEBN/blob/master/figures/iebn.jpg" width="400" height="300">
</p>

## Requirement
* Python 3.6 and [PyTorch 1.0](http://pytorch.org/)

## Usage
  ```
python cifar.py -a iebn_resnet --dataset cifar100 --block-name bottleneck --depth 164 --epochs 164 --schedule 81 122 --gamma 0.1 --wd 1e-4 --checkpoint checkpoints/cifar100/resnet-164-iebn
  ```

## Results
|                 | original |  IEBN  |
|:---------------:|:--------:|:------:|
|    ResNet164    |   74.29  |  77.09 |


**Notes:**
- Training on 2 GPUs

## Citing IEBN

```
@inproceedings{liang2020instance,
  title={Instance Enhancement Batch Normalization: An Adaptive Regulator of Batch Noise.},
  author={Liang, Senwei and Huang, Zhongzhan and Liang, Mingfu and Yang, Haizhao},
  booktitle={AAAI},
  pages={4819--4827},
  year={2020}
}
```

## Acknowledgments
Many thanks to [bearpaw](https://github.com/bearpaw) for his simple and clean [Pytorch framework](https://github.com/bearpaw/pytorch-classification) for image classification task.
