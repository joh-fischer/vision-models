# MIT License Copyright (c) 2022 joh-fischer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import torch
import torch.nn as nn

from models.convnext.ds_conv import DepthwiseSeparableConv
from models.convnext.spatial_layernorm import LayerNorm2D
from models.convnext.stochastic_depth import DropPath


class ConvNeXtBlock(nn.Module):
    def __init__(self, channels: int, kernel_size: int = 7,
                 widening_factor: int = 4, drop_path: float = 0.,
                 eps: float = 1e-6):
        """
        A ConvNeXt block as described in https://arxiv.org/abs/2201.03545,
        with the following structure:
        depthwise-separable convolution -> layer norm -> 1x1 convolution
        with width multiplier -> gelu activation -> 1x1 convolution to
        reduce the channels.

        Args:
            channels: Input and output channels of the block.
            kernel_size: The kernel size for the depthwise-separable
                convolution (default as in the paper: 7)
            widening_factor: Multiplier for the channels in the
                inverted bottleneck 1x1 convolution.
            drop_path: Probability of path dropping (Stochastic Depth).
            eps: Epsilon for layer normalization.
        """
        super().__init__()
        padding = kernel_size // 2
        self.ds_conv = DepthwiseSeparableConv(channels, channels, kernel_size, padding=padding)
        self.norm = LayerNorm2D(channels, eps)
        self.conv1 = nn.Conv2d(channels, channels * widening_factor, kernel_size=1)
        self.gelu = nn.GELU()
        self.conv2 = nn.Conv2d(channels * widening_factor, channels, kernel_size=1)

        self.drop_path = DropPath(drop_path) if drop_path > 0. else nn.Identity()

    def forward(self, x: torch.Tensor):
        residual = x
        x = self.ds_conv(x)
        x = self.norm(x)

        x = self.conv1(x)   # inverted bottleneck
        x = self.gelu(x)

        x = self.conv2(x)   # reduce channels

        x = residual + self.drop_path(x)

        return x


if __name__ == "__main__":
    ipt = torch.randn((8, 16, 32, 32))
    dsc = ConvNeXtBlock(16)

    print("input:", ipt.shape)          # torch.Size([8, 16, 32, 32])
    print("output:", dsc(ipt).shape)    # torch.Size([8, 16, 32, 32])
