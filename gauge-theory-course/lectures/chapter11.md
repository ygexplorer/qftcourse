# 第11章：重整化群

!!! abstract "本章概要"
    本章讨论重整化群（RG）的物理，包括跑动耦合常数和渐近自由。

---

## 11.1 RG 的基本思想

### 尺 度依赖性

重整化后的物理量依赖于**能标** $\mu$：

$$g = g(\mu), \quad m = m(\mu)$$

这是因为我们是在特定能标 $\mu$ 下定义物理可观测量。

### $\beta$ 函数

$$\beta(g) = \mu \frac{\partial g}{\partial \mu}$$

描述耦合常数如何随能标跑动。

---

## 11.2 渐近自由

### 定义

当能标 $\to \infty$ 时，耦合常数 $\to 0$：

$$g(\mu) \to 0 \quad \text{当} \quad \mu \to \infty$$

### QCD 的渐近自由

$$\beta(g) = -\frac{g^3}{16\pi^2}\left(11 - \frac{2N_f}{3}\right) + O(g^5)$$

!!! success " Nobel 奖 (2004)"
    Gross, Wilczek, Politzer 发现渐进自由

### 物理意义

- 高能：夸克和胶子几乎自由（渐近自由）
- 低能：强相互作用增强，夸克禁闭

---

## 11.3 红外不动点

### 定义

$$\beta(g_*) = 0 \quad \text{当} \quad g = g_*$$

### 红外稳定不动点

当 $\beta'(g_*) > 0$，$g_*$ 是红外稳定不动点。

---

## 11.4 Callan-Symanzik 方程

描述两点格林函数随能标的变化：

$$\left[ \mu \frac{\partial}{\partial \mu} + \beta(g) \frac{\partial}{\partial g} + n \gamma(g) \right] G^{(n)} = 0$$

其中 $\gamma(g)$ 是反常维度。

---

## 本章小结

| 概念 | 含义 |
|------|------|
| $\beta$ 函数 | 耦合常数的能标依赖 |
| 渐近自由 | 高能弱耦合（QCD） |
| 红外不动点 | 低能标度的行为 |
| Callan-Symanzik | 格林函数的变化方程 |

---

## 📚 关联章节

- **[[第10章：重整化]]**：重整化的基础

---

*本章内容待补充*
