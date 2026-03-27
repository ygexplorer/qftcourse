# 第2章：路径积分量子化

> **前置知识**：[[第1章：基础回顾]]

!!! abstract "本章概要"
    本章介绍独立于正则量子化的另一种方案——路径积分。它的核心思想是粒子/场会遍历所有可能的历史路径，量子效应是"涌现"出来的。对于具有复杂约束的规范场论，路径积分是更方便的量子化工具。

---

## 2.1 基础思想：从点粒子到场

### 量子力学的路径积分表述

Feynman 提出：粒子从初态 $|x_i\rangle$ 到末态 $|x_f\rangle$ 的跃迁振幅，是所有可能路径的贡献之和：

$$\langle x_f | x_i \rangle = \int \mathcal{D}x(t) \, e^{iS[x(t)]}$$

其中 $S = \int L\,dt$ 是经典作用量。

!!! quote "Feynman 的核心洞察"
    "粒子走所有可能的路径，每条路径贡献一个相位因子 $e^{iS}$，量子干涉决定最终概率。"

---

## 2.2 点粒子的路径积分推导

### 时间切片方法

将时间区间 $[0,T]$ 分割为 $N+1$ 个时刻：

$$U(x_I, x_F; T) = \lim_{N\to\infty} \int \prod_{i=1}^{N-1} dx_i \prod_{j=1}^{N} \langle x_j | x_{j-1} \rangle$$

插入动量完备基，积掉坐标得到高斯积分：

$$\int_{-\infty}^{\infty} dp \, e^{ip\Delta x - i\frac{p^2}{2m}\Delta t} = \sqrt{\frac{2m\pi i}{T}}$$

### 最终结果

$$U(x_F, x_I; T) = \sqrt{\frac{m}{2\pi i T}} \exp\left[ \frac{im(x_F-x_I)^2}{2T} \right]$$

这是自由粒子的传播子。

---

## 2.3 标量场的路径积分

### 生成泛函 $Z[J]$

配分函数（生成泛函）是路径积分的核心：

$$Z[J] = \int \mathcal{D}\phi \, \exp\left( i \int d^4x \, [\mathcal{L}(\phi) + J(x)\phi(x)] \right)$$

其中 $J(x)$ 是外源。

### 格林函数的产生

通过对 $J(x)$ 求泛函导数，可以"拉下"场 $\phi$，从而得到格林函数：

$$\langle 0 | T \phi(x_1) \phi(x_2) \cdots | 0 \rangle = \left. \frac{1}{i^n} \frac{\delta^n Z[J]}{\delta J(x_1) \cdots \delta J(x_n)} \right|_{J=0}$$

---

## 2.4 SD 方程的路径积分推导

!!! success "全课"Aha!"时刻"
    只需做变量代换，利用测度不变性，展开到一阶，**三行公式直接得出 SD 方程**！

对生成泛函做泛函导数：

$$Z[J] = \int \mathcal{D}\phi \, e^{iS[\phi] + i\int J\phi}$$

令 $\phi \to \phi + \delta\phi$，利用测度不变性：

$$\int \mathcal{D}\phi \, \frac{\delta S}{\delta\phi} e^{iS} = 0$$

这正是 SD 方程的路径积分形式！

!!! tip "优雅对比"
    - **算符推导**：需要小心翼翼处理不对易的算符和时间排序
    - **路径积分推导**：场只是普通的积分变量（数），仅用了一次积分变量代换

同理可以推导出 **Ward 等式**，体现路径积分在处理对称性时的强大。

---

## 2.5 费米子与 Grassmann 数

### 反对易数

费米子需要引入**反对易**的 Grassmann 数 $\psi$：

$$\psi_1 \psi_2 = -\psi_2 \psi_1, \quad \psi^2 = 0$$

!!! warning "费米积分的关键性质"
    雅可比行列式的**倒置**性质：

    $$\frac{\partial(\eta, \xi)}{\partial(\theta, \phi)} = 1 \quad \Rightarrow \quad \text{det}\left(\frac{\partial \eta}{\partial \theta}\right) = \text{det}\left(\frac{\partial \phi}{\partial \psi}\right)^{-1}$$

    正是这个倒置，让费米子闭圈多一个负号，也是规范场论中引入 **Ghost 场**的数学基础。

### Berezin 积分规则

$$\int d\eta \, \eta = 1, \quad \int d\eta = 0$$

---

## 2.6 本章小结

| 主题 | 关键点 |
|------|--------|
| 路径积分思想 | 遍历所有历史，相干叠加 |
| 生成泛函 $Z[J]$ | 格林函数的母函数 |
| SD 方程推导 | 变量代换 + 测度不变性，极简 |
| Grassmann 数 | 反对易性，闭圈多一个负号 |

---

## 📚 关联章节

- **[[第1章：基础回顾]]**：正则量子化回顾，为本 章做铺垫
- **[[第4章：规范场的量子化]]**：法捷耶夫-波波夫方法，鬼场的引入

---

## ❓ 思考题

1. 画出点粒子路径积分的时间切片示意图。
2. 用路径积分方法证明自由标量场的传播子。
3. 为什么说"测度不变性"是路径积分的核心优势？
4. Grassmann 数的 $\psi^2 = 0$ 对应什么物理直觉？

---

*本章内容待补充更多细节*
