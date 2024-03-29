# -*- coding: utf-8 -*-
"""Copy of Multi_Class_Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vJvJOrWx9wdSrQBCliLSPrXZH6zpf6Y8

#### **Loading and processing data**

**Notes:** \
Veri yükleme aşamaları gerçekleşti bunlar tensore çevrildi.\
Orijinal test veri kümesi yüklendi burda validation seti olmadığı için val_index ve test_index olarak iki gruba ayrıld.Eğitim sırasında modelin değerlendirilmesi için val_ds kullanılacak. \
"""

from torchvision import datasets
import torchvision.transforms as transforms
import os

#Load the Tra-Data
path2data = "./data"
if not os.path.exists(path2data):
  os.mkdir(path2data)

data_transformer = transforms.Compose([transforms.ToTensor()])

train_ds = datasets.STL10(path2data,split = 'train',
                          download = True,
                          transform = data_transformer)
print(train_ds.data.shape)

#Count number of images per category in train_ds

import collections

y_train = [y for _,y in train_ds]
counter_train = collections.Counter(y_train)
print(counter_train)

#load test_data
test0_ds = datasets.STL10(path2data,split='test',
                          download = True,
                          transform = data_transformer)
print(test0_ds.data.shape)

#Next, split the indices of test0_ds into two groups

from sklearn.model_selection import StratifiedShuffleSplit # kontrol et

sss = StratifiedShuffleSplit(n_splits = 1,test_size = 0.2,
                             random_state = 0)

indices = list(range(len(test0_ds)))
y_test0 = [y for _,y in test0_ds]
for test_index, val_index in sss.split(indices,y_test0):
  print("test:",test_index, 'val:', val_index)
  print(len(val_index),len(test_index))

# create two datasets from test0_ds
from torch.utils.data import Subset # Kontrol et
val_ds = Subset(test0_ds,val_index)
test_ds = Subset(test0_ds,test_index)

#count the number of images per class in val_ds and test_ds:
import collections
import numpy as np

y_test = [y for _,y in test_ds]
y_val = [y for _,y in val_ds ]

counter_test = collections.Counter(y_test)
counter_val = collections.Counter(y_val)
print(counter_test)
print(counter_val)

# Commented out IPython magic to ensure Python compatibility.
#show a few sample images from train_ds. We will import the required
from torchvision import utils
import matplotlib.pyplot as plt
import numpy as np
# %matplotlib inline

np.random.seed(0)

def show(img,y = None,color =True):
  npimg = img.numpy()
  npimg_tr = np.transpose(npimg,(1,2,0))
  plt.imshow(npimg_tr)
  if y is not None:
    plt.title('label: '+str(y))

#pick random samples:
grid_size = 4
rnd_inds = np.random.randint(0,len(train_ds), grid_size)
print("image indices: ", rnd_inds)

x_grid = [train_ds[i][0] for i in rnd_inds]
y_grid = [train_ds[i][1] for i in rnd_inds]

x_grid = utils.make_grid(x_grid, nrow =4,padding  = 1)
print(x_grid.shape)

#call helper function
plt.figure(figsize = (10,10))
show(x_grid,y_grid)

#show sample images from val_ds
np.random.seed(0)

grid_size = 4
rnd_inds = np.random.randint(0,len(val_ds),grid_size)

x_grid = [val_ds[i][0] for i in rnd_inds]
y_grid = [val_ds[i][1] for i in rnd_inds]

x_grid = utils.make_grid(x_grid,nrow = 4, padding = 2)
print(x_grid.shape)

plt.figure(figsize = (10,10))
show(x_grid,y_grid)

#calculate the mean and standard deviation of train_ds
import numpy as np

meanRGB = [np.mean(x.numpy(), axis = (1,2)) for x,_ in train_ds]
stdRGB = [np.std(x.numpy(), axis = (1,2)) for x,_ in train_ds]

meanR=np.mean([m[0] for m in meanRGB])
meanG=np.mean([m[1] for m in meanRGB])
meanB=np.mean([m[2] for m in meanRGB])

stdR=np.mean([s[0] for s in stdRGB])
stdG=np.mean([s[1] for s in stdRGB])
stdB=np.mean([s[2] for s in stdRGB])
print(meanR,meanG,meanB)
print(stdR,stdG,stdB)

# define the image transformations for train_ds and test0_ds:

train_transformer = transforms.Compose([
    transforms.RandomHorizontalFlip(p =0.5),
    transforms.RandomVerticalFlip(p = 0.5),
    transforms.ToTensor(),
    transforms.Normalize([meanR,meanG,meanB],
                         [stdR,stdG,stdB])])
test0_transformer = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([meanR,meanG,meanB],
                         [stdR,stdG,stdB])
])

#Update the transform function of train_ds and test0_ds

train_ds.transform = train_transformer
test0_ds.transform = test0_transformer

#display the transformed sample images from train_d

import torch
np.random.seed(0)
torch.manual_seed(0)

grid_size = 4
rnd_inds = np.random.randint(0,len(train_ds),grid_size)
print("image indices:",rnd_inds)

x_grid = [train_ds[i][0] for i in rnd_inds]
y_grid = [train_ds[i][1] for i in rnd_inds]

x_grid = utils.make_grid(x_grid,nrow = 4, padding = 2)
print(x_grid.shape)

plt.figure(figsize = (10,10))
show(x_grid,y_grid)

# create dataloaders from train_ds and val_ds

from torch.utils.data import DataLoader
train_dl = DataLoader(train_ds, batch_size = 32, shuffle = True)
val_dl = DataLoader(val_ds, batch_size= 32, shuffle = False)

# get a batch of data from train_dl

for x, y in train_dl:
  print(x.shape)
  print(y.shape)
  break

# get a batch of data from val_dl
for x,y in val_dl:
  print(x.shape)
  print(y.shape)
  break

"""#### **Building Model**
**Notes:** \
*pretrained = False* yaparak model ağırlıkları rastgele şekilde başlatılacaktır. \
2.adımda modeli yazdırdık. Görüldüğü gibi son katman 1000 çıktılı doğrusal bir katmandır.Resnet18 modeli 1.000 sınıfa sahip ImageNet veri seti için geliştirilmiştir. Bu nedenle 3. adımda sınıflandırma görevimiz için son katmanı num_classes = 10 çıktıya sahip olacak şekilde değiştiriyoruz. \
Orijinal görüntü boyutları 96 * 96 olsa da, bunları resnet18 modelinin eğitildiği boyutla aynı olan 224*224 boyutuna yeniden boyutlandırmamız gerekiyor.\
"""

# import the resnet18 model with random weights from torchvision.models:

from torchvision import models
import torch

model_resnet18 = models.resnet18(pretrained= False)
print(model_resnet18)

#change the output layer to 10 classes:
from torch import nn
num_classes = 10
num_ftrs = model_resnet18.fc.in_features
model_resnet18.fc = nn.Linear(num_ftrs,num_classes)
device = torch.device("cuda:0")
model_resnet18.to(device)

from torchsummary import summary
summary(model_resnet18,input_size=(3,224,224),device = device.type)

# Let's visualize the filters of the first CNN layer

for w in model_resnet18.parameters():
  w = w.data.cpu()
  print(w.shape)
  break

min_w = torch.min(w)
w1 = (-1/(2*min_w))*w + 0.5
print(torch.min(w1).item(),torch.max(w1).item())

grid_size = len(w1)
x_grid=[w1[i] for i in range(grid_size)]
x_grid=utils.make_grid(x_grid, nrow=8, padding=1)
print(x_grid.shape)

# call helper function
plt.figure(figsize=(5,5))
show(x_grid)

from torchvision import models
import torch

# load model with pretrained weights
resnet18_pretrained = models.resnet18(pretrained=True)

# change the output layer
num_classes=10
num_ftrs = resnet18_pretrained.fc.in_features
resnet18_pretrained.fc = nn.Linear(num_ftrs, num_classes)

device = torch.device("cuda:0")
resnet18_pretrained.to(device)

# get Conv1 weights
for w in resnet18_pretrained.parameters():
    w=w.data.cpu()
    print(w.shape)
    break

# normalize to [0,1]
min_w=torch.min(w)
w1 = (-1/(2*min_w))*w + 0.5
print(torch.min(w1).item(),torch.max(w1).item())

# make a grid
grid_size=len(w1)
x_grid=[w1[i] for i in range(grid_size)]
x_grid=utils.make_grid(x_grid, nrow=8, padding=1)
print(x_grid.shape)

# call helper function
plt.figure(figsize=(5,5))
show(x_grid)

"""#### **Define Loss Function**
Sınıflandırma görevleri için standart kayıp fonksiyonu: *cross-entropy loss or log loss* \
Ancak kayıp fonksiyonunu tanımlarken model çıktılarının sayısını ve bunların aktivasyon fonksiyonlarını dikkate almamız gerekir. Çok sınıflı sınıflandırma görevleri için çıktıların sayısı sınıfların sayısına ayarlanır. Çıkış aktivasyon fonksiyonu daha sonra kayıp fonksiyonunu belirler

"""

###

loss_func = nn.CrossEntropyLoss(reduction = 'sum')

"""reduction parametresi, bir kayıp fonksiyonunun (loss function) toplam kaybın nasıl hesaplanacağını belirten bir parametredir. Bu parametre, genellikle 'none', 'mean' veya 'sum' değerlerini alabilir.

    'none': Bu durumda, her bir veri noktası için kayıp ayrı ayrı hesaplanır ve bir vektör olarak döndürülür. Yani, her bir örnek için kaybı içeren bir vektör elde edersiniz.

    'mean': Bu durumda, her bir veri noktası için hesaplanan kayıpların ortalaması alınır. Yani, toplam kayıp, örnek sayısına bölünerek ortalama kayıp elde edilir.

    'sum': Bu durumda, her bir veri noktası için hesaplanan kayıplar toplanır. Yani, toplam kayıp elde edilir.
"""

torch.manual_seed(0)

n,c = 4,5
y = torch.randn(n,c,requires_grad= True)
print(y.shape)

loss_func = nn.CrossEntropyLoss(reduction="sum")
target = torch.randint(c,size=(n,))
print(target.shape)

loss = loss_func(y, target)
print(loss.item())

#Let's compute the gradients of loss with respect to y
loss.backward()
print (y.data)

"""#### **Defining the optimizer**"""

from torch import optim
opt = optim.Adam(model_resnet18.parameters(), lr = 1e-4)

# get learning rate
def get_lr(opt):
    for param_group in opt.param_groups:
        return param_group['lr']
current_lr = get_lr(opt)
print(f"current_lr = {current_lr}")

# Define a learning scheduler using the CosineAnnealingLR method:

from torch.optim.lr_scheduler import CosineAnnealingLR

lr_scheduler = CosineAnnealingLR(opt,T_max = 2, eta_min = 1e-5)

lrs=[]
for i in range(10):
    lr_scheduler.step()
    lr=get_lr(opt)
    print("epoch %s, lr: %.1e" %(i,lr))
    lrs.append(lr)

plt.plot(lrs)

"""#### **Training and transfer learning**"""

# develop a helper function to count the number of correct predictions per data batch:

def metrics_batch(output,target):
  # get output class
  pred = output.argmax(dim = 1, keepdim = True)
  # compare output class with target class
  corrects = pred.eq(target.view_as(pred)).sum().item()
  return corrects

# develop a helper function to compute the loss value per batch of data:

def loss_batch(loss_func,output,target, opt = None):

  # get loss
  loss = loss_func(output,target)

  # get performance metric
  metric_b = metrics_batch(output, target)

  if opt is not None:
    opt.zero_grad()
    loss.backward()
    opt.step()

  return loss.item(), metric_b

device = torch.device("cuda")

def loss_epoch(model,loss_func, dataset_dl,sanity_check = False, opt = None):
  running_loss = 0.0
  running_metric = 0.0
  len_data = len(dataset_dl.dataset)

  for xb,yb in dataset_dl:
    # move batch to device
    xb = xb.to(device)
    yb = yb.to(device)

    # get model output
    output = model(xb)

    # get loss per batch
    loss_b, metric_b = loss_batch(loss_func,output, yb, opt)

    # update running loss
    running_loss+=loss_b

    # update running metric
    if metric_b is not None:
      running_metric += metric_b

    # break the loop in case of sanity check
    if sanity_check is True:
      break

    # average loss value
    loss=running_loss/float(len_data)

    # average metric value
    metric=running_metric/float(len_data)

    return loss, metric

def train_val(model,params):
  # extract model parameters
  num_epochs=params["num_epochs"]
  loss_func=params["loss_func"]
  opt=params["optimizer"]
  train_dl=params["train_dl"]
  val_dl=params["val_dl"]
  sanity_check=params["sanity_check"]
  lr_scheduler=params["lr_scheduler"]
  path2weights=params["path2weights"]

  # history of loss values in each epoch
  loss_history = {
      "train": [],
      "val": []
  }

  # history of metric values in each epoch
  metric_history = {
      "train": [],
      "val": [],
  }
  # a deep copy of weights for best performing model

  best_model_wts = copy.deepcopy(model.state_dict)

  #initialize best loss to a large value
  best_loss = float("inf")

  for epoch in range(num_epochs):

    # get current learning rate
    current_lr = get_lr(opt)
    print('Epoch {}/{}, current lr ={}'.format(epoch,num_epochs -1, current_lr))

    model.train()
    train_loss,train_metric = loss_epoch(model, loss_func, train_dl,sanity_check, opt)

    # collect loss and metric for training dataset
    loss_history["train"].append(train_loss)
    metric_history["train"].append(train_metric)

    # evaluate model on validation dataset
    model.eval()
    with torch.no_grad():
      val_loss, val_metric = loss_epoch(model, loss_func, val_dl, sanity_check)

    # store best model
    if val_loss  < best_loss:
      best_loss = val_loss
      best_model_wts = copy.deepcopy(model.state_dict())

      # store weights into a local file

      torch.save(model.state_dict(), path2weights)
      print("Copied best model weights")

    # collect loss and metric for validation dataset
    loss_history["val"].append(val_loss)
    metric_history["val"].append(val_metric)

    lr_scheduler.step()
    print("train loss: %.6f, dev loss: %.6f, accuracy: %.2f" %(train_loss,val_loss,100*val_metric))
    print("-"*10)

    # load best model weights
    model.load_state_dict(best_model_wts)

    return model, loss_history, metric_history

"""##Train With Random-Init Weights"""

#We will redefine the loss, optimizer, and learning rate schedule
import copy

loss_func = nn.CrossEntropyLoss(reduction = 'sum')
opt = optim.Adam(model_resnet18.parameters(), lr = 1e-4)
lr_scheduler = CosineAnnealingLR(opt,T_max = 5, eta_min= 1e-6)
#CosineAnnealingLR PyTorch'daki bir öğrenme oranı zamanlayıcıdır.
#eta_min: Bu, öğrenme oranının minimum değerini belirler.
#T_max parametresi, öğrenme oranının maksimum değerini koruyacağı epoch sayısını belirler

params_train={
 "num_epochs": 3,
 "optimizer": opt,
 "loss_func": loss_func,
 "train_dl": train_dl,
 "val_dl": val_dl,
 "sanity_check": False,
 "lr_scheduler": lr_scheduler,
 "path2weights": "./models/resnet18.pt",
}

# train and validate the model
model_resnet18,loss_hist,metric_hist=train_val(model_resnet18,params_train)

num_epochs = params_train["num_epochs"]

plt.title("Train-val Loss")
plt.plot(range(1,num_epochs+1),loss_hist['train'],label = 'train')
plt.plot(range(1,num_epochs+1),loss_hist["val"], label = 'val')
plt.ylabel("Loss")
plt.xlabel("Training Epochs")
plt.legend()
plt.show()

