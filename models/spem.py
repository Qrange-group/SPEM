from __future__ import absolute_import
import torch
import torch.nn as nn
from torch.nn.parameter import Parameter
import math


__all__ = ["spem"]


def conv3x3(in_planes, out_planes, stride=1):
    "3x3 convolution with padding"
    return nn.Conv2d(
        in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=False
    )


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, downsample=None, info="normal"):
        super(Bottleneck, self).__init__()
        self.info = info
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(
            planes, planes, kernel_size=3, stride=stride, padding=1, bias=False
        )
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

        self.num_pool = 2
        self.w1 = Parameter(torch.Tensor(1, planes * 4, 1, 1))
        self.b1 = Parameter(torch.Tensor(1, planes * 4, 1, 1))
        self.w1.data.fill_(0)
        self.b1.data.fill_(-1)
        self.w2 = Parameter(torch.Tensor(1, planes * 4, 1, 1))
        self.b2 = Parameter(torch.Tensor(1, planes * 4, 1, 1))
        self.w2.data.fill_(0)
        self.b2.data.fill_(-1)
        self.GlobalMax = nn.AdaptiveMaxPool2d((1, 1))
        self.p = Parameter(torch.Tensor(self.num_pool))
        nn.init.constant_(self.p, 1 / self.num_pool)
        self.sigmoid = nn.Sigmoid()
        self.softmax = nn.Softmax()

    def forward(self, x):
        x, pm_sum = x
        residual = x
        out = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        # attention logic
        original_out = out  # torch.Size([16, 256, 8, 8]) outshape
        max = self.GlobalMax(out)
        min = out.min(dim=(-1), keepdim=True)
        min = min.values.min(dim=(-2), keepdim=True).values
        max = max * self.w2 + self.b2
        min = min * self.w2 + self.b2

        p_pow = torch.pow(self.p, 2)
        p = p_pow / torch.sum(p_pow)
        mix = p[0] * max + p[1] * min
        mix = mix * self.w1 + self.b1

        out = self.sigmoid(min + max) * self.sigmoid(mix) * original_out

        out += residual
        out = self.relu(out)
        return (out, torch.pow(self.p, 2).sum() + pm_sum)


class SPEM(nn.Module):
    def __init__(self, depth, num_classes=1000, block_name="BasicBlock", info="normal"):
        super(SPEM, self).__init__()
        # Model type specifies number of layers for CIFAR-10 model
        if block_name.lower() == "basicblock":
            assert (
                depth - 2
            ) % 6 == 0, "When use basicblock, depth should be 6n+2, e.g. 20, 32, 44, 56, 110, 1202"
            n = (depth - 2) // 6
            block = BasicBlock
        elif block_name.lower() == "bottleneck":
            assert (
                depth - 2
            ) % 9 == 0, "When use bottleneck, depth should be 9n+2, e.g. 20, 29, 47, 56, 110, 1199"
            n = (depth - 2) // 9
            block = Bottleneck
        else:
            raise ValueError("block_name shoule be Basicblock or Bottleneck")

        self.inplanes = 16
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(16)
        self.relu = nn.ReLU(inplace=True)
        self.layer1 = self._make_layer(block, 16, n, info=info)
        self.layer2 = self._make_layer(block, 32, n, stride=2, info=info)
        self.layer3 = self._make_layer(block, 64, n, stride=2, info=info)
        self.avgpool = nn.AvgPool2d(8)
        self.fc = nn.Linear(64 * block.expansion, num_classes)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2.0 / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def _make_layer(self, block, planes, blocks, stride=1, info="normal"):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:  # 16=?planes*4
            downsample = nn.Sequential(
                nn.Conv2d(
                    self.inplanes,
                    planes * block.expansion,
                    kernel_size=1,
                    stride=stride,
                    bias=False,
                ),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample, info=info))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes, info=info))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)  # 32x32

        x = self.layer1((x, 0))  # 32x32
        x = self.layer2(x)  # 16x16
        x, pm = self.layer3(x)  # 8x8

        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x, pm


def spem(**kwargs):
    """
    Constructs a ResNet model.
    """
    return SPEM(**kwargs)
