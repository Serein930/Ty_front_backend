<template>
  <aside class="w-[420px] bg-midBlue/95 border-r border-primary/20 flex flex-col z-40 backdrop-blur-md shadow-xl overflow-hidden shrink-0">
    <div class="p-4 border-b border-white/10">
      <h3 class="text-xs font-bold text-textGray uppercase mb-2 flex items-center">
        <i class="fa-solid fa-gavel mr-2"></i>研判结论与案件元数据
      </h3>
      <div class="verdict-card rounded-lg p-4" :class="`theme-${theme}`" id="verdict-container">
        <slot name="verdict"></slot>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
      <div>
        <h3 class="text-xs font-bold text-textGray uppercase mb-2 flex justify-between items-center pb-1 border-b border-gray-600/50">
          <span><i class="fa-solid fa-users mr-2"></i>核心骨干画像 (HUMINT)</span>
          <span class="bg-white/10 px-1.5 py-0.5 rounded text-[10px]">{{ memberCount }}</span>
        </h3>
        <div class="space-y-3">
          <slot name="members"></slot>
        </div>
      </div>

      <div class="space-y-4">
        <div class="bg-propaganda/5 border border-propaganda/20 rounded p-2">
          <div class="flex justify-between items-center mb-1.5">
            <span class="text-[10px] text-propaganda uppercase font-bold">
              <i class="fa-solid fa-bullhorn mr-1"></i>公域与暗网渠道
            </span>
            <span class="text-[10px] text-gray-400">{{ propagandaCount }}</span>
          </div>
          <div class="space-y-1">
            <slot name="propaganda"></slot>
          </div>
        </div>

        <div>
          <div class="flex justify-between items-center mb-1.5">
            <span class="text-[10px] text-warning uppercase font-bold">
              <i class="fa-solid fa-coins mr-1"></i>黑资洗白/钱包
            </span>
            <span class="text-[10px] text-gray-500">{{ financeCount }}</span>
          </div>
          <div class="space-y-1">
            <slot name="finance"></slot>
          </div>
        </div>

        <div>
          <div class="flex justify-between items-center mb-1.5">
            <span class="text-[10px] text-traffic uppercase font-bold">
              <i class="fa-solid fa-server mr-1"></i>C2与网络资产
            </span>
            <span class="text-[10px] text-gray-500">{{ trafficCount }}</span>
          </div>
          <div class="space-y-1">
            <slot name="traffic"></slot>
          </div>
        </div>

        <div>
          <div class="flex justify-between items-center mb-1.5">
            <span class="text-[10px] text-material uppercase font-bold">
              <i class="fa-solid fa-file-code mr-1"></i>关键物料/载荷/物流
            </span>
            <span class="text-[10px] text-gray-500">{{ materialCount }}</span>
          </div>
          <div class="space-y-1">
            <slot name="material"></slot>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  theme: {
    type: String,
    default: 'terrorism'
  },
  memberCount: {
    type: Number,
    default: 0
  },
  propagandaCount: {
    type: Number,
    default: 0
  },
  financeCount: {
    type: Number,
    default: 0
  },
  trafficCount: {
    type: Number,
    default: 0
  },
  materialCount: {
    type: Number,
    default: 0
  }
});
</script>

