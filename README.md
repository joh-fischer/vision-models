# Image Classification Models

Implementation of a few popular vision models in PyTorch. 


## Results

Results of some trainings on `CIFAR10`. Each model is trained with AdamW optimizer for 60 epochs using
a cosine decay learning rate scheduler and 10 epochs linear warm-up. Please note, that the reported
accuracies are far from what is possible with those models. I just trained them for a couple of
epochs and didn't finetune them at all. ;)


|                           Paper                            |          Code           |  Params   | Accuracy |
|:----------------------------------------------------------:|:-----------------------:|:---------:|:--------:|
|         [ResNet](https://arxiv.org/abs/1512.03385)         | [resnet](models/resnet) |  175,594  |  95.2%   |
|          [ViT](https://arxiv.org/abs/2010.11929)           |    [vit](models/vit)    |  305,802  |  60.7%   |
| [Hierarchical Perceiver](https://arxiv.org/abs/2202.10890) |    [hip](models/hip)    | 1,204,138 |  52.6%   |

## Usage

You can train the models with

```
python3 main.py resnet --name exp1 --epochs 60 --batch-size 256 --warmup-epochs 10
```

A list of supported models can be found in the results section (*code* column).

### ResNet

He et al. ([2016](https://arxiv.org/abs/1512.03385)) introduced skip connections
to build deeper models.

```python
from models import ResNet

model = ResNet()

x = torch.randn((64, 3, 32, 32))
model(x).shape      # [64, 10] 
```

### ViT

Dosovitskiy et al. ([2020](https://arxiv.org/abs/2010.11929)) propose the Vision Transformer (ViT), which
simply applies the NLP Transformer Encoder to images.

```python
from models import ViT

model = ViT()

x = torch.randn((64, 3, 32, 32))
model(x).shape      # [64, 10] 
```

### Hierarchical Perceiver

Carreira et al. ([2022](https://arxiv.org/abs/2202.10890)) improve the efficiency of the Perceiver
by making it hierarchical. For that, the authors propose the HiP-Block which divides the input
sequence into groups and independently applies cross- and self-attention to those groups. Stacking
multiple of those blocks results in the respective hierarchy.

```python
import yaml
from models import HierarchicalPerceiver

cfg = yaml.load(open('configs/hip.yaml', 'r'), Loader=yaml.Loader)
model = HierarchicalPerceiver(**cfg)

x = torch.randn((64, 3, 32, 32))
model(x).shape      # [64, 10] 
```

For this implementation I used standard 2D sinusoidal instead of learned positional embeddings. Furthermore, I only
train on classification with the HiP encoder. However, you can add the decoder simply by editing the
config file of the HiP (add some more blocks with decreasing `latent_dim` and increasing sequence length). Then
the proposed masked auto-encoder pre-training ([MAE](https://arxiv.org/abs/2111.06377)) is quite
straight-forward.
