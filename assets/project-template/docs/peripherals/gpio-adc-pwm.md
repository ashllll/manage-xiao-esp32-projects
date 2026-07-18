# GPIO、ADC 与 PWM

## GPIO

```c
#include "driver/gpio.h"
#include "xiao_pins.h"

gpio_config_t cfg = {
    .pin_bit_mask = 1ULL << XIAO_D3,
    .mode = GPIO_MODE_INPUT,
    .pull_up_en = GPIO_PULLUP_ENABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type = GPIO_INTR_NEGEDGE,
};
ESP_ERROR_CHECK(gpio_config(&cfg));
```

机械按键需要去抖。中断服务只通知任务，不执行 I²C/SPI、日志洪泛或长时间计算。外部电路必须保证上电和复位期间的电平不会破坏启动配置。

## ADC oneshot

ADC 引脚、单元、通道和可测范围因芯片而异，不能只凭“D0 是模拟口”硬编码通道。使用 ESP-IDF 的 ADC oneshot driver，并为每个板型建立 GPIO 到 ADC unit/channel 的经过验证映射。

```c
#include "esp_adc/adc_oneshot.h"

adc_oneshot_unit_handle_t unit;
adc_oneshot_unit_init_cfg_t unit_cfg = {
    .unit_id = ADC_UNIT_1,
};
ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit_cfg, &unit));

adc_oneshot_chan_cfg_t chan_cfg = {
    .atten = ADC_ATTEN_DB_12,
    .bitwidth = ADC_BITWIDTH_DEFAULT,
};
ESP_ERROR_CHECK(adc_oneshot_config_channel(unit, channel, &chan_cfg));
```

原始 ADC 数值不是精确电压。需要电压值时使用校准驱动，并记录衰减、分压、参考误差、输入阻抗、采样平均和温度条件。信号不得超过 GPIO 允许范围。

## PWM / LEDC

LEDC 通过 timer 定义频率/分辨率，通过 channel 连接 GPIO：

```c
#include "driver/ledc.h"

ledc_timer_config_t timer = {
    .speed_mode = LEDC_LOW_SPEED_MODE,
    .timer_num = LEDC_TIMER_0,
    .duty_resolution = LEDC_TIMER_12_BIT,
    .freq_hz = 5000,
    .clk_cfg = LEDC_AUTO_CLK,
};
ESP_ERROR_CHECK(ledc_timer_config(&timer));

ledc_channel_config_t channel_cfg = {
    .gpio_num = XIAO_D3,
    .speed_mode = LEDC_LOW_SPEED_MODE,
    .channel = LEDC_CHANNEL_0,
    .timer_sel = LEDC_TIMER_0,
    .duty = 0,
};
ESP_ERROR_CHECK(ledc_channel_config(&channel_cfg));
```

频率、分辨率和时钟源互相约束。PWM GPIO 只能输出逻辑信号，驱动电机、灯带或高功率 LED 必须使用外部功率级。

## 资源记录

外设页应记录 GPIO 方向/默认电平、中断边沿、ADC unit/channel/衰减/校准、LEDC timer/channel/频率/分辨率，以及与其他组件的占用关系。

官方参考：

- [GPIO](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html)
- [ADC oneshot](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/adc_oneshot.html)
- [LEDC](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/ledc.html)

最近核对：2026-07-18。
