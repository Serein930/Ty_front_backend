<template>
  <div class="topology-wrapper w-full h-screen overflow-hidden text-white bg-[#051029] text-[14px]">
    <header class="h-14 bg-midBlue border-b border-primary/30 flex items-center px-4 justify-between relative z-50 shadow-lg gap-3 overflow-hidden">
        <div class="flex items-center gap-3 shrink-0">
            <div class="w-9 h-9 rounded bg-primary/20 flex items-center justify-center border border-primary/50 text-primary shrink-0">
                <i class="fa-solid fa-radar text-lg animate-pulse-fast"></i>
            </div>
            <div class="shrink-0">
                <h1 class="font-bold text-lg tracking-wide text-white whitespace-nowrap">天眼情报 <span class="text-primary">OSINT 溯源引擎</span></h1>
                <p class="text-[10px] text-textGray -mt-1 font-mono whitespace-nowrap">EngineCore v9.0 Multi-Dimensional</p>
            </div>
        </div>

        <div class="flex items-center bg-black/40 border border-white/20 rounded-md px-3 py-1.5 ml-4 w-56 min-w-0 focus-within:border-primary focus-within:shadow-glow transition shadow-inner shrink">
            <i class="fa-solid fa-magnifying-glass text-gray-400 text-xs"></i>
            <input type="text" id="global-search" placeholder="在当前图中检索..." class="bg-transparent border-none text-xs text-white outline-none w-full ml-2 font-mono" onkeypress="if(event.key==='Enter') window.executeSearch()">
            <button onclick="window.executeSearch()" class="text-xs text-primary hover:text-white transition" title="执行搜索"><i class="fa-solid fa-crosshairs"></i></button>
        </div>
        
        <div class="flex-1"></div> 

        <div class="flex gap-2 items-center flex-nowrap whitespace-nowrap shrink-0 overflow-x-auto no-scrollbar">
            <router-link to="/dashboard" class="px-3 py-1.5 text-xs rounded hover:bg-white/10 text-gray-400 hover:text-white transition flex items-center gap-1 border border-transparent hover:border-gray-500 mr-1 whitespace-nowrap shrink-0">
                <i class="fa-solid fa-arrow-left"></i> 返回态势
            </router-link>

            <button class="px-3 py-1.5 text-xs rounded bg-white/10 hover:bg-white/20 border border-white/30 text-white font-bold transition flex items-center gap-2 whitespace-nowrap shrink-0" onclick="window.openNewProjectModal()">
                <i class="fa-solid fa-folder-plus text-blue-400"></i> 新建研判专案
            </button>
            <button class="px-3 py-1.5 text-xs rounded bg-white/10 hover:bg-white/20 border border-white/30 text-white font-bold transition flex items-center gap-2 whitespace-nowrap shrink-0" onclick="window.openHistoryModal()">
                <i class="fa-solid fa-clock-rotate-left text-primary"></i> 历史档案库
            </button>
            <div class="w-px h-6 bg-white/20 mx-1 shrink-0"></div>
            
            <div class="flex bg-darkBlue rounded-lg p-1 border border-white/10 shrink-0 whitespace-nowrap">
                <button id="view-all" class="px-3 py-1.5 text-xs rounded bg-primary text-darkBlue font-bold shadow-glow transition-all whitespace-nowrap" onclick="window.switchView('all')"><i class="fa-solid fa-circle-nodes mr-1"></i>全维视界</button>
                <button id="view-finance" class="px-3 py-1.5 text-xs rounded hover:bg-white/10 text-textGray hover:text-warning transition-all whitespace-nowrap" onclick="window.switchView('finance')"><i class="fa-solid fa-money-bill-transfer mr-1"></i>资金</button>
                <button id="view-traffic" class="px-3 py-1.5 text-xs rounded hover:bg-white/10 text-textGray hover:text-traffic transition-all whitespace-nowrap" onclick="window.switchView('traffic')"><i class="fa-solid fa-server mr-1"></i>基建</button>
                <button id="view-propaganda" class="px-3 py-1.5 text-xs rounded hover:bg-white/10 text-textGray hover:text-propaganda transition-all whitespace-nowrap" onclick="window.switchView('propaganda')"><i class="fa-solid fa-bullhorn mr-1"></i>宣发</button>
            </div>
            
            <button class="px-3 py-1.5 text-xs rounded bg-white/10 hover:bg-white/20 border border-white/30 text-white font-bold transition flex items-center gap-2 ml-1 whitespace-nowrap shrink-0" onclick="window.openReportModal()">
                <i class="fa-solid fa-file-contract text-danger"></i> 案卷清单
            </button>
            
            <button class="px-3 py-1.5 text-xs rounded bg-white/10 hover:bg-white/20 border border-white/30 text-white font-bold transition flex items-center gap-2 whitespace-nowrap shrink-0" onclick="window.openManualEntry()">
                <i class="fa-solid fa-pen-to-square text-green-400"></i> 人工录入
            </button>
        </div>

        <div class="flex items-center gap-3 text-sm ml-3 shrink-0 whitespace-nowrap">
            <div class="flex items-center gap-2 cursor-pointer hover:text-white text-textGray border-l border-white/20 pl-3 whitespace-nowrap">
                <img src="/offline/avatar-default.svg" class="w-6 h-6 rounded-full border border-gray-500">
                <span class="text-xs whitespace-nowrap">分析师 (04291)</span>
            </div>
        </div>
    </header>

    <div class="flex h-[calc(100vh-3.5rem)] relative overflow-hidden">
        <aside class="w-[420px] bg-midBlue/95 border-r border-primary/20 flex flex-col z-40 backdrop-blur-md shadow-xl overflow-hidden shrink-0">
            <div class="p-4 border-b border-white/10">
                <h3 class="text-xs font-bold text-textGray uppercase mb-2 flex items-center"><i class="fa-solid fa-gavel mr-2"></i>研判结论与案件元数据</h3>
                <div class="verdict-card rounded-lg p-4" id="verdict-container"></div>
            </div>

            <div class="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
                <div>
                    <h3 class="text-xs font-bold text-textGray uppercase mb-2 flex justify-between items-center pb-1 border-b border-gray-600/50">
                        <span><i class="fa-solid fa-users mr-2"></i>核心骨干画像 (HUMINT)</span>
                        <span class="bg-white/10 px-1.5 py-0.5 rounded text-[10px]" id="member-count">0</span>
                    </h3>
                    <div class="space-y-3" id="member-list"></div>
                </div>
                
                <div class="space-y-4">
                    <div class="bg-propaganda/5 border border-propaganda/20 rounded p-2"><div class="flex justify-between items-center mb-1.5"><span class="text-[10px] text-propaganda uppercase font-bold"><i class="fa-solid fa-bullhorn mr-1"></i>公域与暗网渠道</span><span class="text-[10px] text-gray-400" id="propaganda-count">0</span></div><div id="entity-list-propaganda" class="space-y-1"></div></div>
                    <div><div class="flex justify-between items-center mb-1.5"><span class="text-[10px] text-warning uppercase font-bold"><i class="fa-solid fa-coins mr-1"></i>黑资洗白/钱包</span><span class="text-[10px] text-gray-500" id="finance-count">0</span></div><div id="entity-list-finance" class="space-y-1"></div></div>
                    <div><div class="flex justify-between items-center mb-1.5"><span class="text-[10px] text-traffic uppercase font-bold"><i class="fa-solid fa-server mr-1"></i>C2与网络资产</span><span class="text-[10px] text-gray-500" id="traffic-count">0</span></div><div id="entity-list-traffic" class="space-y-1"></div></div>
                    <div><div class="flex justify-between items-center mb-1.5"><span class="text-[10px] text-material uppercase font-bold"><i class="fa-solid fa-file-code mr-1"></i>关键物料/载荷/物流</span><span class="text-[10px] text-gray-500" id="material-count">0</span></div><div id="entity-list-material" class="space-y-1"></div></div>
                </div>
            </div>
        </aside>

        <main class="flex-1 bg-darkBlue bg-grid relative overflow-hidden flex flex-col">
            <div id="engine-loader" class="absolute inset-0 z-50 bg-black/80 flex flex-col items-center justify-center hidden">
                <div class="w-24 h-24 relative mb-6">
                    <div class="absolute inset-0 border-4 border-t-primary border-r-primary border-b-transparent border-l-transparent rounded-full animate-spin"></div>
                    <div class="absolute inset-2 border-4 border-l-warning border-b-warning border-t-transparent border-r-transparent rounded-full animate-spin-slow"></div>
                    <i class="fa-solid fa-radar absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-3xl text-white"></i>
                </div>
                <h2 class="text-xl font-bold text-white tracking-widest mb-2" id="loader-title">OSINT 引擎加载中...</h2>
                <p class="text-xs text-primary font-mono" id="loader-status">正在解析初始目标指纹...</p>
                <div class="w-64 h-1 bg-gray-800 mt-4 overflow-hidden rounded"><div class="loader-bar" id="loader-bar"></div></div>
            </div>

            <div id="task-queue-panel" class="absolute top-16 right-4 z-40 w-72 space-y-2 pointer-events-none flex flex-col items-end"></div>
            <div id="toast-container" class="absolute bottom-6 right-6 z-50 space-y-2 pointer-events-none flex flex-col items-end"></div>

            <div class="absolute top-4 left-4 bg-black/60 border border-white/10 p-3 rounded-lg z-20 backdrop-blur-md shadow-lg pointer-events-none opacity-90 transition-opacity hover:opacity-100">
                <h4 class="text-[10px] font-bold text-gray-400 mb-2 uppercase border-b border-white/10 pb-1 flex items-center"><i class="fa-solid fa-list mr-1"></i>本体图例 (Legend)</h4>
                <div class="grid grid-cols-2 gap-x-6 gap-y-2 text-[10px] text-gray-300 font-mono">
                    <div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 rounded-full border border-[#ffcc00] bg-[#0b1b38] flex items-center justify-center text-[6px] text-[#ffcc00]"><i class="fa-solid fa-coins"></i></div>涉资 (Wallet)</div>
                    <div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 rounded-full border border-[#ff9500] bg-[#0b1b38] flex items-center justify-center text-[6px] text-[#ff9500]"><i class="fa-solid fa-server"></i></div>基建 (C2/IP)</div>
                    <div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 rounded-full border border-[#bd00ff] bg-[#0b1b38] flex items-center justify-center text-[6px] text-[#bd00ff]"><i class="fa-solid fa-file-code"></i></div>物料/物流</div>
                    <div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 rounded-full border border-[#d946ef] bg-[#0b1b38] flex items-center justify-center text-[6px] text-[#d946ef]"><i class="fa-solid fa-bullhorn"></i></div>公宣渠道</div>
                    <div class="flex items-center gap-1.5"><div class="w-4 h-[2px] bg-danger"></div>核心控制/指令</div>
                    <div class="flex items-center gap-1.5"><div class="w-4 h-[2px] bg-propaganda border-t-2 border-dashed"></div>跨域引流/分发</div>
                </div>
            </div>

            <div id="graph-container" class="w-full h-full cursor-move outline-none relative"></div>
            
            <div id="canvas-tooltip" class="absolute hidden bg-panelBg border border-primary/50 text-white p-2.5 rounded shadow-glow text-xs pointer-events-none z-50 transition-opacity duration-150 backdrop-blur-md" style="max-width: 280px; transform: translate(-50%, -100%); margin-top: -10px;"></div>

            <div id="batch-fab" class="absolute bottom-24 left-1/2 transform -translate-x-1/2 bg-[#0a192f]/95 border border-[#00f0ff] text-white px-5 py-2.5 rounded-full shadow-[0_0_20px_rgba(0,240,255,0.4)] z-40 transition-all duration-300 translate-y-32 opacity-0 flex items-center gap-4 backdrop-blur-md">
                <span class="text-[11px] font-bold tracking-widest uppercase text-gray-300"><i class="fa-solid fa-object-group text-primary mr-1.5"></i>已锁定框选: <span id="batch-count" class="text-primary text-base mx-1 font-mono">0</span> 项</span>
                <div class="w-px h-5 bg-white/20 mx-1"></div>
                <button class="text-[11px] font-bold bg-white/10 hover:bg-white/20 border border-white/20 px-3 py-1.5 rounded transition shadow" onclick="alert('模块载入中：已准备将选中实体打包入卷。')"><i class="fa-solid fa-file-contract mr-1"></i> 批量入卷</button>
                <button class="text-xs text-gray-400 hover:text-white px-2 py-1 ml-2 transition" onclick="window.clearBrushSelection()" title="取消框选"><i class="fa-solid fa-xmark"></i></button>
            </div>

            <div id="topology-filters" class="absolute bottom-8 right-8 flex flex-col gap-3 z-30">
                <button class="w-10 h-10 bg-midBlue/90 backdrop-blur border border-white/20 rounded-full hover:border-green-400 hover:text-green-400 transition shadow-lg flex items-center justify-center group relative" onclick="window.saveLayout()" title="保存当前画布布局坐标"><i class="fa-solid fa-floppy-disk"></i></button>
                <button class="w-10 h-10 bg-midBlue/90 backdrop-blur border border-white/20 rounded-full hover:border-blue-400 hover:text-blue-400 transition shadow-lg flex items-center justify-center group relative" onclick="window.loadLayout()" title="加载已存的画布布局"><i class="fa-solid fa-upload"></i></button>
                <div class="w-10 h-px bg-white/20 my-1"></div>
                <button id="btn-brush-mode" class="w-10 h-10 bg-midBlue/90 backdrop-blur border border-white/20 rounded-full hover:border-primary hover:text-primary transition shadow-lg flex items-center justify-center group relative" onclick="window.toggleBrushMode()" title="开启/关闭实体战术框选 (Brush)"><i class="fa-solid fa-object-group"></i></button>
                <button class="w-10 h-10 bg-midBlue/90 backdrop-blur border border-white/20 rounded-full hover:border-primary hover:text-primary transition shadow-lg flex items-center justify-center" onclick="window.resetZoom()" title="缩放自适应重置"><i class="fa-solid fa-compress"></i></button>
                <button class="w-10 h-10 bg-midBlue/90 backdrop-blur border border-white/20 rounded-full hover:border-warning hover:text-warning transition shadow-lg flex items-center justify-center" onclick="window.togglePhysics()" title="暂停/恢复力导向引力"><i class="fa-solid fa-pause" id="physics-icon"></i></button>
            </div>

            <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 bg-panelBg backdrop-blur-md p-4 rounded-xl border border-primary/30 shadow-glow flex flex-col gap-2 w-1/3 min-w-[450px] z-30 transition-transform duration-300" id="timeline-container">
                <div class="flex justify-between items-center text-[11px] font-bold text-textGray">
                    <span id="time-start">--</span>
                    <span id="time-current" class="text-white text-sm bg-primary/20 border border-primary/50 px-3 py-1 rounded-full shadow-glow">--</span>
                    <span id="time-end">--</span>
                </div>
                <input type="range" id="timeline-slider" class="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-primary" min="0" max="100" value="100">
                <div class="text-center text-[10px] text-gray-400 mt-1 uppercase tracking-widest"><i class="fa-solid fa-clock-rotate-left mr-1"></i> 证据链时间轴推演</div>
            </div>
        </main>

        <aside id="details-panel" class="absolute top-0 right-0 h-full w-[500px] bg-panelBg border-l border-primary/20 transform translate-x-full panel-slide flex flex-col z-50 backdrop-blur-xl shadow-2xl">
            <div id="details-content" class="flex-1 flex flex-col h-full relative"></div>
        </aside>
    </div>

    <div id="history-modal" class="hidden fixed inset-0 z-[120] bg-black/90 flex items-center justify-center backdrop-blur-md">
        <div class="bg-midBlue border border-primary/50 rounded-xl w-[700px] flex flex-col shadow-[0_0_50px_rgba(0,240,255,0.3)] overflow-hidden">
            <div class="p-5 border-b border-white/10 flex justify-between items-center bg-black/40">
                <h2 class="text-lg font-bold text-white tracking-wider flex items-center gap-2"><i class="fa-solid fa-clock-rotate-left text-primary"></i> 调阅历史归档专案</h2>
                <button onclick="window.closeHistoryModal()" class="text-gray-400 hover:text-white text-xl"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="p-6 h-[400px] overflow-y-auto custom-scrollbar">
                <p class="text-xs text-gray-400 mb-4">系统已缓存以下重大安全事件的完整证据链图谱。点击恢复沙盘：</p>
                <div class="grid grid-cols-1 gap-3">
                    <div class="border border-white/10 bg-black/40 p-3 rounded-lg flex items-center justify-between hover:border-red-500/50 hover:bg-red-900/10 cursor-pointer transition group" onclick="window.triggerScenarioLoad('terrorism')"><div class="flex items-center gap-3"><div class="w-10 h-10 rounded-full bg-red-500/20 text-red-500 flex items-center justify-center"><i class="fa-solid fa-skull"></i></div><div><div class="font-bold text-white group-hover:text-red-400 transition">918特大连环暴恐袭击案</div><div class="text-[10px] text-gray-500">实体: 7 | 涵盖暗网招募、USDT洗钱与炸药前体采购。</div></div></div><i class="fa-solid fa-chevron-right text-gray-600 group-hover:text-red-400"></i></div>
                    <div class="border border-white/10 bg-black/40 p-3 rounded-lg flex items-center justify-between hover:border-blue-500/50 hover:bg-blue-900/10 cursor-pointer transition group" onclick="window.triggerScenarioLoad('smuggling')"><div class="flex items-center gap-3"><div class="w-10 h-10 rounded-full bg-blue-500/20 text-blue-500 flex items-center justify-center"><i class="fa-solid fa-ship"></i></div><div><div class="font-bold text-white group-hover:text-blue-400 transition">猎狐行动：跨国豪车走私网络</div><div class="text-[10px] text-gray-500">实体: 6 | 涵盖货运提单伪造、空壳公司与离岸对公账户。</div></div></div><i class="fa-solid fa-chevron-right text-gray-600 group-hover:text-blue-400"></i></div>
                    <div class="border border-white/10 bg-black/40 p-3 rounded-lg flex items-center justify-between hover:border-purple-500/50 hover:bg-purple-900/10 cursor-pointer transition group" onclick="window.triggerScenarioLoad('narcotics')"><div class="flex items-center gap-3"><div class="w-10 h-10 rounded-full bg-purple-500/20 text-purple-500 flex items-center justify-center"><i class="fa-solid fa-pills"></i></div><div><div class="font-bold text-white group-hover:text-purple-400 transition">暗网网络贩毒与加密资产洗白</div><div class="text-[10px] text-gray-500">实体: 5 | 涵盖 Tor 市场、混币器、马仔物流分发。</div></div></div><i class="fa-solid fa-chevron-right text-gray-600 group-hover:text-purple-400"></i></div>
                </div>
            </div>
        </div>
    </div>

    <div id="new-project-modal" class="hidden fixed inset-0 z-[120] bg-black/90 flex items-center justify-center backdrop-blur-md">
        <div class="bg-midBlue border border-primary/50 rounded-xl w-[800px] flex flex-col shadow-[0_0_50px_rgba(0,240,255,0.3)] overflow-hidden">
            <div class="p-5 border-b border-white/10 flex justify-between items-center bg-black/40">
                <h2 class="text-lg font-bold text-white tracking-wider flex items-center gap-2"><i class="fa-solid fa-folder-plus text-primary"></i> 开启全新研判专案</h2>
                <button onclick="window.closeNewProjectModal()" class="text-gray-400 hover:text-white text-xl"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="p-6 flex flex-col overflow-y-auto max-h-[70vh] custom-scrollbar">
                <h3 class="text-xs font-bold text-primary mb-3 border-b border-primary/30 pb-1">1. 案件基础元数据 (Metadata)</h3>
                <div class="grid grid-cols-2 gap-4 mb-6">
                    <div class="col-span-2"><label class="text-[10px] font-bold text-gray-400 uppercase">专案名称 (Project Name) <span class="text-danger">*</span></label><input type="text" id="proj-name" class="analyst-input text-sm mt-1" placeholder="例如: 918跨国地下钱庄网络追踪案" value="未命名侦察专案"></div>
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">案件分类 (Category)</label><select id="proj-category" class="analyst-input text-sm mt-1"><option value="INTEL_TERRORISM">暴恐与极端组织 (Terrorism)</option><option value="INTEL_SMUGGLING">跨国走私与黑产 (Smuggling)</option><option value="INTEL_NARCOTICS">毒品与暗网黑市 (Narcotics)</option></select></div>
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">初始威胁定级 (Threat Level)</label><select id="proj-level" class="analyst-input text-sm mt-1"><option value="S">S 级 (国家级/极高危)</option><option value="A" selected>A 级 (高危跨域网络)</option><option value="B">B 级 (区域性团伙)</option></select></div>
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">创建/主研判人</label><input type="text" class="analyst-input text-sm mt-1 bg-black/50" value="分析师 (04291)" disabled readonly></div>
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">案件卷宗号 (自动生成)</label><input type="text" id="proj-id" class="analyst-input text-sm mt-1 bg-black/50 font-mono text-gray-500" disabled readonly></div>
                    <div class="col-span-2"><label class="text-[10px] font-bold text-gray-400 uppercase">立案简述 (Description)</label><textarea id="proj-desc" rows="2" class="analyst-input text-xs mt-1" placeholder="简要描述案件背景或研判目标..."></textarea></div>
                </div>

                <h3 class="text-xs font-bold text-warning mb-3 border-b border-warning/30 pb-1"><i class="fa-solid fa-seedling mr-1"></i>2. 初始情报探针配置 (Seed Injection)</h3>
                <div class="bg-warning/5 border border-warning/20 p-4 rounded-lg space-y-4">
                    <p class="text-[11px] text-gray-400 leading-tight">系统需要一个确切的“落脚点”作为图谱生长的种子。请输入已掌握的关键账号、钱包或网络资产，引擎将自下而上进行特征穿透与扩线。</p>
                    <div><label class="text-[10px] font-bold text-white uppercase">初始线索标识 (Target Value) <span class="text-danger">*</span></label><input type="text" id="seed-input" class="analyst-input text-base mt-1 border-warning/50 focus:border-warning" placeholder="例如: @ShadowHacker99 或 0x1A2B3C..." value="@Suspect_Target_01"></div>
                    <div class="grid grid-cols-2 gap-4">
                        <div><label class="text-[10px] font-bold text-gray-400 uppercase">线索属性 (Type)</label><select id="seed-type" class="analyst-input text-sm mt-1"><option value="social_public">社交媒体/暗网账号 (Social)</option><option value="wallet">加密资产地址 (Crypto Wallet)</option><option value="traffic">网络资产 (IP/Domain)</option></select></div>
                        <div><label class="text-[10px] font-bold text-gray-400 uppercase">自动扩线深度 (Hops)</label><select class="analyst-input text-sm mt-1"><option>仅录入不扩线</option><option selected>自动深挖 2度关联 (推荐)</option><option>自动深挖 3度穿透 (耗时)</option></select></div>
                    </div>
                </div>
                
                <div class="mt-8 flex gap-3">
                    <button class="flex-1 bg-gray-800 hover:bg-gray-700 text-white py-3 rounded-lg font-bold text-sm transition" onclick="window.closeNewProjectModal()">取消立案</button>
                    <button class="flex-[2] bg-primary hover:bg-primary/80 text-darkBlue py-3 rounded-lg font-bold text-sm shadow-[0_0_15px_rgba(0,240,255,0.4)] transition transform hover:scale-[1.02] flex items-center justify-center gap-2" onclick="window.submitNewProject()">
                        <i class="fa-solid fa-bolt"></i> 创建专案并挂起扩线任务
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div id="report-modal" class="hidden fixed inset-0 z-[100] bg-black/80 flex items-center justify-center backdrop-blur-sm">
        <div class="bg-midBlue border border-primary/50 rounded-xl w-[90%] max-w-6xl flex flex-col shadow-[0_0_50px_rgba(0,240,255,0.3)] max-h-[85vh] overflow-hidden">
            <div class="p-4 border-b border-white/10 flex justify-between items-center bg-black/40">
                <h2 class="text-lg font-bold text-white tracking-wider flex items-center gap-2">
                    <i class="fa-solid fa-file-contract text-primary"></i> 法庭级证据链生成清单 
                    <span class="text-xs text-gray-500 font-mono ml-2"> 生成时间: <span id="report-generate-time"></span></span>
                </h2>
                <div class="flex items-center gap-3">
                    <button onclick="window.exportReportCSV()" class="text-xs bg-green-500/20 hover:bg-green-500/40 text-green-400 border border-green-500/50 px-3 py-1.5 rounded transition shadow-glow-green"><i class="fa-solid fa-file-csv mr-1"></i> 导出 CSV</button>
                    <button onclick="window.print()" class="text-xs bg-primary/20 hover:bg-primary/40 text-primary border border-primary/50 px-3 py-1.5 rounded transition shadow-glow"><i class="fa-solid fa-print mr-1"></i> 导出为 PDF 卷宗</button>
                    <button onclick="window.closeReportModal()" class="text-gray-400 hover:text-white text-xl ml-2"><i class="fa-solid fa-xmark"></i></button>
                </div>
            </div>
            <div class="flex-1 overflow-auto p-5 custom-scrollbar bg-darkBlue">
                <table class="w-full text-left border-collapse report-table">
                    <thead><tr><th class="text-primary font-bold text-xs uppercase tracking-wider">发现时间</th><th class="text-primary font-bold text-xs uppercase tracking-wider">证据编号</th><th class="text-primary font-bold text-xs uppercase tracking-wider">证据链推演 (Source -> Target)</th><th class="text-primary font-bold text-xs uppercase tracking-wider">采集方式 / 来源</th><th class="text-primary font-bold text-xs uppercase tracking-wider text-center">置信度</th><th class="text-primary font-bold text-xs uppercase tracking-wider">源数据哈希校验 (Hash)</th><th class="text-primary font-bold text-xs uppercase tracking-wider text-center">操作</th></tr></thead>
                    <tbody id="report-table-body"></tbody>
                </table>
            </div>
        </div>
    </div>

    <div id="raw-evidence-modal" class="hidden fixed inset-0 z-[110] bg-black/90 flex items-center justify-center backdrop-blur-md">
        <div class="bg-midBlue border border-primary/50 rounded-lg w-[1100px] h-[85vh] flex flex-col shadow-[0_0_40px_rgba(0,240,255,0.4)] overflow-hidden">
            <div class="p-0 border-b border-white/10 flex flex-col bg-black/40">
                <div class="p-4 flex justify-between items-center"><h2 class="text-sm font-bold text-white tracking-wider flex items-center gap-2"><i class="fa-solid fa-file-shield text-primary"></i> Evidence Capsule (多模态取证包快照查阅器)</h2><button onclick="window.closeRawEvidence()" class="text-gray-400 hover:text-white text-xl"><i class="fa-solid fa-xmark"></i></button></div>
                <div class="flex px-4 gap-2 border-t border-white/5 bg-black/20" id="ev-tabs-container">
                    <button id="ev-tab-snapshot" class="ev-tab active flex items-center gap-2" onclick="window.switchEvidenceTab('snapshot')"><i class="fa-solid fa-camera-retro"></i> 原始快照与元数据</button>
                    <button id="ev-tab-llm" class="ev-tab flex items-center gap-2 hidden" onclick="window.switchEvidenceTab('llm')"><i class="fa-solid fa-brain text-green-400"></i> LLM 智能提纯沙箱</button>
                </div>
            </div>
            <div id="evidence-modal-body" class="flex-1 flex overflow-hidden relative">
                <div id="ev-pane-snapshot" class="w-full flex h-full"></div>
                <div id="ev-pane-llm" class="w-full h-full hidden flex"></div>
            </div>
        </div>
    </div>

    <div id="manual-entry-modal" class="hidden fixed inset-0 z-[120] bg-black/80 flex items-center justify-center backdrop-blur-sm">
        <div class="bg-midBlue border border-primary/50 rounded-xl w-[500px] flex flex-col shadow-[0_0_50px_rgba(0,240,255,0.3)] overflow-hidden transition-all duration-300">
            <div class="p-4 border-b border-white/10 flex justify-between items-center bg-black/40">
                <h2 class="text-sm font-bold text-white tracking-wider flex items-center gap-2"><i class="fa-solid fa-pen-to-square text-primary"></i> 人工情报录入 (Manual Entry)</h2>
                <button onclick="window.closeManualEntry()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            
            <div class="flex p-4 gap-2 border-b border-white/10 bg-black/20">
                <button id="tab-add-node" class="flex-1 py-1.5 text-xs bg-blue-600 text-white rounded border border-blue-500 font-bold transition" onclick="window.switchEntryTab('node')">录入新实体</button>
                <button id="tab-add-link" class="flex-1 py-1.5 text-xs bg-black/40 text-gray-400 rounded border border-white/10 hover:text-white transition" onclick="window.switchEntryTab('link')">建立新关联</button>
                <button id="tab-add-batch" class="flex-1 py-1.5 text-xs bg-black/40 text-gray-400 rounded border border-white/10 hover:text-white transition" onclick="window.switchEntryTab('batch')">批量上传解析</button>
            </div>
            
            <div class="p-5">
                <div id="form-add-node" class="space-y-4">
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">实体大类</label><select id="new-node-category" class="analyst-input text-sm mt-1 h-9" onchange="window.updateSubtypeOptions()"><option value="user">人员/组织 (User)</option><option value="wallet">加密资产 (Wallet)</option><option value="traffic">网络资产 (Traffic)</option><option value="social">社交/暗网账号 (Social)</option><option value="material">涉案物料/物流 (Material/Logistics)</option></select></div>
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">具体子类型</label><select id="new-node-subtype" class="analyst-input text-sm mt-1 h-9"></select></div>
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">标识/名称 (Value/Name)</label><input type="text" id="new-node-value" class="analyst-input text-sm mt-1 h-9" placeholder="例如: 张三 或 0x123..."></div>
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">情报来源 (Source)</label><input type="text" id="new-node-source" class="analyst-input text-sm mt-1 h-9" placeholder="例如: 审讯笔录 / 匿名线报"></div>
                </div>
                
                <div id="form-add-link" class="space-y-4 hidden">
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">起点实体 (Source)</label><select id="new-link-source" class="analyst-input text-sm mt-1 h-9"></select></div>
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">动作/本体 (Predicate)</label><select id="new-link-predicate" class="analyst-input text-sm mt-1 h-9"></select></div>
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">终点实体 (Target)</label><select id="new-link-target" class="analyst-input text-sm mt-1 h-9"></select></div>
                    <div><label class="text-[10px] font-bold text-gray-400 uppercase">研判置信度 (Confidence)</label><input type="number" id="new-link-conf" class="analyst-input text-sm mt-1 h-9" min="0.1" max="1.0" step="0.1" value="0.8"></div>
                </div>

                <div id="form-add-batch" class="hidden">
                    <div class="border-2 border-dashed border-primary/50 rounded-lg p-6 text-center cursor-pointer hover:border-primary hover:bg-primary/5 transition group relative" onclick="document.getElementById('batch-file-upload').click()">
                        <i class="fa-solid fa-cloud-arrow-up text-4xl text-primary mb-3 group-hover:-translate-y-2 transition-transform shadow-glow"></i>
                        <div class="text-sm font-bold text-white mb-1 tracking-wide">点击上传或拖拽原始文件至此处</div>
                        <div class="text-[11px] text-gray-400">支持 .pdf, .docx, .png, .txt, .eml 格式</div>
                        <div class="mt-4 bg-primary/10 border border-primary/20 p-2 rounded text-[10px] text-primary flex items-start gap-1.5 text-left"><i class="fa-solid fa-wand-magic-sparkles mt-0.5"></i><span>基于大模型的多模态自动清洗：文件上传后，将唤起 <strong>LLM 智能提纯沙箱</strong>。您可以对 AI 提取出的高危实体(钱包、账号等)进行人工确认与校对，随后一键固化至图谱。</span></div>
                        <input type="file" id="batch-file-upload" class="hidden" onchange="window.triggerBatchLLMSandbox()">
                    </div>
                </div>
            </div>
            
            <div class="p-4 border-t border-white/10 bg-black/40 flex justify-end gap-3" id="manual-entry-actions">
                <button class="px-4 py-1.5 text-xs text-gray-400 hover:text-white transition" onclick="window.closeManualEntry()">取消</button>
                <button id="manual-entry-submit-btn" class="px-4 py-1.5 text-xs bg-primary text-darkBlue font-bold rounded shadow-glow hover:bg-primary/80 transition" onclick="window.submitManualEntry()">确认录入并重绘</button>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';
import * as d3 from 'd3';
import { scenarioDB, predicateMap } from '../mock/topologyData.js'; 

onMounted(() => {
    // 💡 核心奥义：将所有 Vue 和外部作用域的对象挂载到 window
    // 使得模板中所有的 onclick="window.xxx()" 依然能够完美执行原生逻辑！
    window.d3 = d3;
    window.scenarioDB = scenarioDB;
    window.predicateMap = predicateMap;

    function generateNodeTimeline(node) {
        const events = [];
        if (node.provenance && node.provenance.time) {
            events.push({ time: parseTime(node.provenance.time), type: 'node', desc: `首次发现于 ${escapeHTML(node.provenance.source || '未知来源')}`, rawTime: node.provenance.time });
        }
        const links = nodeLinksMap[node.id] || [];
        links.forEach(link => {
            if (!link.timestamp) return;
            const isSource = getSafeNodeId(link.source) === node.id;
            const otherId = isSource ? getSafeNodeId(link.target) : getSafeNodeId(link.source);
            const otherNode = fusionData.nodes.find(n => n.id === otherId);
            const otherName = otherNode ? (otherNode.name || otherNode.label || otherNode.value) : '未知实体';
            const predZh = predicateMap[link.predicate]?.zh || link.predicate;
            events.push({ time: parseTime(link.timestamp), type: 'link', desc: isSource ? `作为源，通过 [${predZh}] 关联至 ${escapeHTML(otherName)}` : `作为目标，被 ${escapeHTML(otherName)} 通过 [${predZh}] 关联`, rawTime: link.timestamp, linkId: link.evidence_id });
        });
        events.sort((a, b) => b.time - a.time);
        if (events.length === 0) return '<div class="text-xs text-gray-500 italic">暂无时序事件</div>';
        return events.map(ev => {
            const timeStr = ev.rawTime || new Date(ev.time).toLocaleString();
            const clickAttr = ev.linkId ? `onclick="window.findAndShow('${ev.linkId}', 'link'); event.stopPropagation();"` : '';
            return `<div class="flex items-start gap-3 text-xs border-l-2 border-primary/30 pl-2 py-1 hover:bg-white/5 rounded cursor-pointer transition" ${clickAttr}><span class="text-[10px] text-gray-500 font-mono whitespace-nowrap">${timeStr}</span><span class="text-gray-300 leading-tight">${ev.desc}</span></div>`;
        }).join('');
    }

    function escapeHTML(str) {
        if (str == null) return '';
        return String(str).replace(/[&<>"]/g, function(match) {
            if (match === '&') return '&amp;'; if (match === '<') return '&lt;'; if (match === '>') return '&gt;'; if (match === '"') return '&quot;'; return match;
        });
    }

    const getSafeNodeId = (d) => typeof d === 'object' ? d.id : d;
    const getSafeNodeObj = (d) => typeof d === 'object' ? d : fusionData.nodes.find(n => n.id === d);
    const parseTime = (ts) => { if (!ts) return minTime; let tStr = ts.replace(' ', 'T'); if (!tStr.includes('T')) tStr += "T00:00:00"; return new Date(tStr).getTime(); };

    const subtypeOptions = {
        user: [ { value: 'leader', label: '头目/核心' }, { value: 'finance', label: '财务人员' }, { value: 'logistics', label: '物流人员' }, { value: 'member', label: '普通成员' }, { value: 'contact', label: '联系人/中间人' } ],
        wallet: [ { value: 'BTC', label: '比特币地址 (BTC)' }, { value: 'ETH', label: '以太坊地址 (ETH)' }, { value: 'USDT', label: 'USDT (ERC20/TRC20)' }, { value: 'XMR', label: '门罗币 (XMR)' }, { value: 'bank_account', label: '银行账户' }, { value: 'card', label: '银行卡/预付卡' } ],
        traffic: [ { value: 'IP', label: 'IP地址' }, { value: 'DOMAIN', label: '域名' }, { value: 'URL', label: 'URL链接' }, { value: 'C2', label: 'C2服务器' }, { value: 'TOR_HIDDEN', label: 'Tor隐藏服务 (.onion)' }, { value: 'I2P', label: 'I2P站点' } ],
        social: [ { value: 'TELEGRAM', label: 'Telegram账号' }, { value: 'DISCORD', label: 'Discord账号' }, { value: 'TWITTER', label: 'Twitter/X账号' }, { value: 'FACEBOOK', label: 'Facebook账号' }, { value: 'INSTAGRAM', label: 'Instagram账号' }, { value: 'DARKWEB_FORUM', label: '暗网论坛账号' }, { value: 'WECHAT', label: '微信账号' } ],
        material: [ { value: 'CONTAINER', label: '集装箱 (Container ISO6346)' }, { value: 'PARCEL', label: '快递包裹 (Tracking #)' }, { value: 'CHEMICAL', label: '化学品/前体' }, { value: 'WEAPON', label: '武器/爆炸物' }, { value: 'VEHICLE', label: '车辆' }, { value: 'DOCUMENT', label: '伪造文件/提单' } ]
    };

    window.updateSubtypeOptions = function() {
        const category = document.getElementById('new-node-category').value;
        const subtypeSelect = document.getElementById('new-node-subtype');
        subtypeSelect.innerHTML = '';
        (subtypeOptions[category] || []).forEach(opt => { const option = document.createElement('option'); option.value = opt.value; option.textContent = opt.label; subtypeSelect.appendChild(option); });
    };

    let fusionData = null; let currentSelectedData = null, currentItemType = null; let minTime, maxTime, currentTimeValue; let currentView = 'all'; let isBrushMode = false;
    let simulation, svg, gTopology, zoomBehavior; let linkSelection, nodeSelection; let width = 800, height = 600; let adjOutgoing = {}, nodeLinksMap = {}; let currentExtractionSourceId = null;

    const toggleModal = (id, show) => document.getElementById(id).classList.toggle('hidden', !show);

    window.openHistoryModal = () => toggleModal('history-modal', true);
    window.closeHistoryModal = () => toggleModal('history-modal', false);
    window.closeNewProjectModal = () => toggleModal('new-project-modal', false);
    window.closeReportModal = () => toggleModal('report-modal', false);
    window.closeRawEvidence = () => toggleModal('raw-evidence-modal', false);
    window.closeManualEntry = () => toggleModal('manual-entry-modal', false);

    window.showEngineLoader = (title, status) => {
        const loader = document.getElementById('engine-loader');
        if (title) document.getElementById('loader-title').innerText = title;
        if (status) document.getElementById('loader-status').innerText = status;
        loader.classList.remove('hidden');
        const bar = document.getElementById('loader-bar'); if(bar) { bar.style.width = '0%'; setTimeout(() => { bar.style.width = '100%'; }, 50); }
    };
    window.hideEngineLoader = () => document.getElementById('engine-loader').classList.add('hidden');

    window.updateThemeByScenario = (scenarioKey) => { const c = document.getElementById('verdict-container'); if (c) c.className = `verdict-card rounded-lg p-4 theme-${scenarioKey}`; };

    window.addExtractionTaskToPanel = (taskId, targetValue) => {
        const panel = document.getElementById('task-queue-panel'); if (!panel) return;
        const taskDiv = document.createElement('div'); taskDiv.id = taskId; taskDiv.className = "bg-black/80 border border-primary/50 text-white p-2 rounded text-xs flex items-center gap-2 shadow-glow"; taskDiv.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin text-primary"></i> <span>探针穿透中: ${escapeHTML(targetValue)}</span>`;
        panel.appendChild(taskDiv);
    };

    window.removeExtractionTaskFromPanel = (taskId) => { const taskDiv = document.getElementById(taskId); if (taskDiv) taskDiv.remove(); };

    window.showIntelToast = (message, type = 'info') => {
        const container = document.getElementById('toast-container'); if (!container) return;
        const toast = document.createElement('div');
        let colorClass = type === 'success' ? 'text-green-400 border-green-500/50 bg-green-900/20 shadow-glow-green' : (type === 'info' ? 'text-primary border-primary/50 bg-darkBlue/90 shadow-glow' : 'text-danger border-danger/50 bg-red-900/20 shadow-glow-danger');
        toast.className = `border p-3 rounded shadow-lg text-xs transform transition-all duration-300 translate-x-full flex items-start gap-2 max-w-sm backdrop-blur-md ${colorClass} mb-2`;
        let icon = type === 'success' ? 'fa-circle-check' : (type === 'info' ? 'fa-circle-info' : 'fa-triangle-exclamation');
        toast.innerHTML = `<i class="fa-solid ${icon} mt-0.5 text-base"></i><div class="leading-relaxed font-mono">${escapeHTML(message)}</div>`;
        container.appendChild(toast); setTimeout(() => toast.classList.remove('translate-x-full'), 50);
        setTimeout(() => { toast.classList.add('translate-x-full'); setTimeout(() => toast.remove(), 300); }, 3500);
    };
    
    window.openNewProjectModal = () => { document.getElementById('proj-id').value = "OP-" + new Date().getFullYear() + "-" + Math.floor(Math.random()*10000); toggleModal('new-project-modal', true); setTimeout(() => document.getElementById('proj-name').focus(), 100); };

    window.submitNewProject = () => {
        const pName = document.getElementById('proj-name').value.trim(); const pCat = document.getElementById('proj-category').value; const pLevel = document.getElementById('proj-level').value; const pDesc = document.getElementById('proj-desc').value.trim(); const seedVal = document.getElementById('seed-input').value.trim(); const seedType = document.getElementById('seed-type').value;
        if(!pName || !seedVal) return alert("带星号（*）的字段为必填项！"); window.closeNewProjectModal();
        fusionData = { meta: { group_id: document.getElementById('proj-id').value, category: pCat, category_label: pName, level: pLevel, risk_score: 0, description: pDesc || "基于人工注入的情报种子动态扩线生成的拓扑图谱。" }, sourceRegistry: { "SRC-DYN": { type: "OSINT/全网", name: "天眼动态爬虫集群", reliability: "B", frequency: "实时", desc: "基于 API 与无头浏览器的即时抓取。" } }, nodes: [], links: [] };
        initGraph(); window.updateThemeByScenario('dynamic');
        const taskId = 'TASK-' + Math.floor(Math.random() * 10000); window.addExtractionTaskToPanel(taskId, seedVal); window.showIntelToast(`立案成功！系统已派发异步探针，深度追踪目标 [${seedVal}]...`, 'info');
        setTimeout(() => {
            window.removeExtractionTaskFromPanel(taskId);
            const nowStr = new Date().toISOString().replace('T', ' ').substring(0, 16);
            let seedNode = { id: "dyn_seed", type: seedType, subtype: "TARGET", value: seedVal, label: "🎯 " + seedVal.substring(0, 15), risk: "HIGH", location: "Proxy IP", provenance: { source: "探针入口", time: nowStr, telemetry: { funnel_stage: "RECON", route_corridor: "AUTO_DISCOVERY", query_family: "SEED_INJECT" } } };
            const newNodes = [ seedNode, { id: "dyn_u1", type: "user", role: "leader", name: "Hidden_Admin", location: "SE Asia", avatar: "/offline/avatar-default.svg", score: 88, risk: "CRITICAL", provenance: { source: "流量还原", time: nowStr } }, { id: "dyn_e1", type: "wallet", subtype: "USDT", value: "0xDynWallet", label: "💰 隐藏资金池", risk: "HIGH", location: "Proxy IP", provenance: { source: "链上监测", time: nowStr } } ];
            const newLinks = [ { source: "dyn_u1", target: "dyn_seed", type: "command", predicate: "ACCOUNT_LOGIN", evidence_id: "D-L1", timestamp: nowStr, conf: 0.95 }, { source: "dyn_seed", target: "dyn_e1", type: "referral", predicate: "BIO_LINK", evidence_id: "D-L2", timestamp: nowStr, conf: 0.9 } ];
            fusionData.nodes.push(...newNodes); fusionData.links.push(...newLinks);
            preprocessData(); initGraph(); window.showIntelToast(`🎯 扩线预警：[${seedVal}] 任务完成，成功涌现 ${newNodes.length} 个新实体及关联！`, 'success');
            const cloneData = { meta: fusionData.meta, sourceRegistry: fusionData.sourceRegistry, nodes: fusionData.nodes, links: fusionData.links.map(l => ({ ...l, source: typeof l.source === 'object' ? l.source.id : l.source, target: typeof l.target === 'object' ? l.target.id : l.target })) };
            const newScenarioKey = 'dynamic_' + Date.now(); scenarioDB[newScenarioKey] = JSON.parse(JSON.stringify(cloneData));
            const historyContainer = document.querySelector('#history-modal .grid');
            if (historyContainer) {
                const newCard = document.createElement('div'); newCard.className = "border border-white/10 bg-black/40 p-3 rounded-lg flex items-center justify-between hover:border-green-500/50 hover:bg-green-900/10 cursor-pointer transition group"; newCard.onclick = () => window.triggerScenarioLoad(newScenarioKey);
                newCard.innerHTML = `<div class="flex items-center gap-3"><div class="w-10 h-10 rounded-full bg-green-500/20 text-green-500 flex items-center justify-center"><i class="fa-solid fa-bolt"></i></div><div><div class="font-bold text-white group-hover:text-green-400 transition">${escapeHTML(pName)}</div><div class="text-[10px] text-gray-500">实体: ${fusionData.nodes.length} | 手工创建与探针扩线。</div></div></div><i class="fa-solid fa-chevron-right text-gray-600 group-hover:text-green-400"></i>`;
                historyContainer.insertBefore(newCard, historyContainer.firstChild);
            }
        }, 3000);
    };

    window.triggerScenarioLoad = (scenarioKey) => {
        window.closeHistoryModal(); window.showEngineLoader(`正在调阅【${scenarioDB[scenarioKey].meta.category_label}】卷宗...`, "重建多维态势数据立方体...");
        setTimeout(() => { fusionData = JSON.parse(JSON.stringify(scenarioDB[scenarioKey])); initGraph(); const themeKey = scenarioKey.startsWith('dynamic') ? 'dynamic' : scenarioKey; window.updateThemeByScenario(themeKey); window.hideEngineLoader(); }, 1200);
    };

    function dragstarted(event, d) { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }
    function dragged(event, d) { d.fx = event.x; d.fy = event.y; }
    function dragended(event, d) { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }

    window.resetZoom = () => { if(svg && zoomBehavior) svg.transition().duration(750).call(zoomBehavior.transform, d3.zoomIdentity); };

    window.togglePhysics = () => {
        const icon = document.getElementById('physics-icon');
        if (simulation.alpha() > 0) { simulation.stop(); icon.classList.replace('fa-pause', 'fa-play'); } 
        else { simulation.alpha(0.3).restart(); icon.classList.replace('fa-play', 'fa-pause'); }
    };
    
    window.saveLayout = () => { window.showIntelToast("坐标布局已保存至本地快照。", "success"); };
    window.loadLayout = () => { window.showIntelToast("已加载上次的画布布局。", "info"); };

    function initGraph() {
        if(simulation) simulation.stop(); generateInferredLinks(); preprocessData();
        const containerDiv = document.getElementById('graph-container'); width = containerDiv.clientWidth; height = containerDiv.clientHeight;
        d3.select("#graph-container").selectAll("svg").remove(); 
        svg = d3.select("#graph-container").append("svg").attr("width", "100%").attr("height", "100%"); gTopology = svg.append("g").attr("class", "layer-topology");
        zoomBehavior = d3.zoom().scaleExtent([0.1, 4]).on("zoom", (e) => gTopology.attr("transform", e.transform)); svg.call(zoomBehavior).on("dblclick.zoom", null);
        const defs = svg.append("defs");
        const markerTypes = [{ id: 'finance', color: '#ffcc00' }, { id: 'logistics', color: '#007aff' }, { id: 'command', color: '#ff3b30' }, { id: 'material', color: '#bd00ff' }, { id: 'traffic', color: '#ff9500' }, { id: 'referral', color: '#d946ef' }];
        markerTypes.forEach(m => defs.append("marker").attr("id", `arrow-${m.id}`).attr("viewBox", "0 -5 10 10").attr("refX", 35).attr("refY", 0).attr("markerWidth", 6).attr("markerHeight", 6).attr("orient", "auto").append("path").attr("d", "M0,-5L10,0L0,5").attr("fill", m.color));
        simulation = d3.forceSimulation(fusionData.nodes).force("link", d3.forceLink(fusionData.links).id(d => d.id).distance(160)).force("charge", d3.forceManyBody().strength(-1500)).force("center", d3.forceCenter(width / 2, height / 2)).force("collide", d3.forceCollide(d => d.collisionRadius || ((d.type === 'user' ? 25 : 20) + (d.degree || 0) * 3 + 15))).force("y", d3.forceY(height/2).strength(0.05)).force("x", d3.forceX(width/2).strength(0.05));
        renderViews(); initTimeline(); populateSidebar(); 
    }

    function renderViews() { gTopology.classed("hidden", false); if(simulation.alpha() < 0.1) simulation.alpha(0.3).restart(); updateGraphElements(); }

    function updateGraphElements() {
        const tooltip = document.getElementById('canvas-tooltip');
        linkSelection = gTopology.selectAll(".link").data(fusionData.links, d => d.evidence_id); linkSelection.exit().remove();
        const linkEnter = linkSelection.enter().insert("path", ".node").attr("class", d => `link link-${d.type || 'command'}`).attr("id", d => `link-${d.evidence_id}`).attr("marker-end", d => `url(#arrow-${d.type || 'command'})`).style("stroke-width", d => (d.type === 'command') ? 2 : 1.5)
            .on("mouseover", function(e, d) { if(!isBrushMode) d3.select(this).transition().duration(200).style("stroke-width", 4).style("opacity", 1); })
           .on("mousemove", function(e, d) {
                if(isBrushMode) return; tooltip.classList.remove('hidden'); 
                const mainRect = document.querySelector('main').getBoundingClientRect();
                let relX = e.clientX - mainRect.left; let relY = e.clientY - mainRect.top;
                tooltip.style.transform = 'none'; tooltip.style.marginTop = '0'; tooltip.style.width = '250px'; tooltip.style.maxWidth = 'none';
                if (relX + 270 > mainRect.width) { tooltip.style.left = 'auto'; tooltip.style.right = (mainRect.width - relX + 15) + 'px'; } else { tooltip.style.right = 'auto'; tooltip.style.left = (relX + 15) + 'px'; }
                if (relY - 120 < 0) { tooltip.style.bottom = 'auto'; tooltip.style.top = (relY + 15) + 'px'; } else { tooltip.style.top = 'auto'; tooltip.style.bottom = (mainRect.height - relY + 15) + 'px'; }
                let pZh = predicateMap[d.predicate]?.zh || d.predicate;
                tooltip.innerHTML = `<div class="font-bold text-primary mb-1 border-b border-primary/30 pb-1 break-all whitespace-normal"><i class="fa-solid fa-link mr-1"></i>${pZh}</div><div class="text-[10px] text-gray-300 leading-tight break-all whitespace-normal">置信度: <span class="${d.conf<0.7?'text-danger':'text-green-400'}">${d.conf}</span><br>时间: ${d.timestamp || '未知'}<br><span class="text-gray-500 font-mono scale-90 block mt-1 break-all">ID: ${d.evidence_id}</span></div>`;
            })
            .on("mouseout", function(e, d) {
                tooltip.classList.add('hidden'); if(isBrushMode) return;
                let w = (d.type === 'command') ? 2 : 1.5; let currentOpacity = 0.05; const linkTime = parseTime(d.timestamp);
                if (linkTime <= currentTimeValue) {
                    let isVisible = true;
                    if (currentView === 'finance' && d.type !== 'finance') isVisible = false; if (currentView === 'logistics' && !['logistics', 'material'].includes(d.type)) isVisible = false; if (currentView === 'traffic' && !['traffic'].includes(d.type)) isVisible = false; if (currentView === 'propaganda' && !['referral', 'command'].includes(d.type)) isVisible = false;
                    if (isVisible) currentOpacity = d.conf < 0.7 ? 0.35 : (d.conf || 1);
                }
                d3.select(this).transition().duration(200).style("stroke-width", w).style("opacity", currentOpacity);
            })
            .on("click", (e, d) => { e.stopPropagation(); if(!isBrushMode) openAnalystPanel(d, 'link'); });
        linkSelection = linkEnter.merge(linkSelection);

        nodeSelection = gTopology.selectAll(".node").data(fusionData.nodes, d => d.id); nodeSelection.exit().remove();
        const nodeEnter = nodeSelection.enter().append("g").attr("class", "node").attr("id", d => `node-${d.id}`).call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended))
            .on("mousemove", function(e, d) {
                if(isBrushMode) return; tooltip.classList.remove('hidden'); 
                const mainRect = document.querySelector('main').getBoundingClientRect();
                let relX = e.clientX - mainRect.left; let relY = e.clientY - mainRect.top;
                tooltip.style.transform = 'none'; tooltip.style.marginTop = '0'; tooltip.style.width = '220px'; tooltip.style.maxWidth = 'none';
                if (relX + 240 > mainRect.width) { tooltip.style.left = 'auto'; tooltip.style.right = (mainRect.width - relX + 15) + 'px'; } else { tooltip.style.right = 'auto'; tooltip.style.left = (relX + 15) + 'px'; }
                if (relY - 100 < 0) { tooltip.style.bottom = 'auto'; tooltip.style.top = (relY + 15) + 'px'; } else { tooltip.style.top = 'auto'; tooltip.style.bottom = (mainRect.height - relY + 15) + 'px'; }
                let name = d.name || d.label || d.value; let isUser = d.type === 'user'; let riskColor = d.risk === 'CRITICAL' ? 'text-danger' : d.risk === 'HIGH' ? 'text-orange-500' : 'text-warning';
                tooltip.innerHTML = `<div class="font-bold ${isUser?'text-white':'text-primary'} mb-1 border-b border-white/20 pb-1 break-all whitespace-normal">${escapeHTML(name)}</div><div class="text-[10px] text-gray-300 leading-tight grid grid-cols-2 gap-1"><span class="truncate" title="本体: ${escapeHTML(d.type)}">本体: ${escapeHTML(d.type)}</span><span class="${riskColor} truncate">风险: ${escapeHTML(d.risk||'N/A')}</span><span class="col-span-2 text-gray-500 truncate mt-1">介数: ${d.betweennessNorm||0}</span></div>`;
            })
            .on("mouseout", () => tooltip.classList.add('hidden'))
            .on("click", (e, d) => { e.stopPropagation(); if (!isBrushMode) openAnalystPanel(d, 'node'); });

        nodeEnter.each(function(d) {
            const el = d3.select(this); const baseR = d.type === 'user' ? 28 : 20; const r = baseR + (d.degree || 0) * 3.5; d.collisionRadius = r + 15;
            if(d.isBridge) el.append("circle").attr("r", r + 6).attr("fill", "none").attr("stroke", "rgba(255,255,255,0.2)").attr("stroke-width", 2).attr("stroke-dasharray", "4 4").attr("class", "animate-spin-slow bridge-ring");
            if (d.type === 'user') {
                svg.select("defs").append("pattern").attr("id", `avatar-${d.id}`).attr("width", 1).attr("height", 1).append("image").attr("href", d.avatar).attr("width", r * 2).attr("height", r * 2).attr("x", 0).attr("y", 0).attr("preserveAspectRatio", "xMidYMid slice");
                el.append("circle").attr("r", r).attr("fill", `url(#avatar-${d.id})`).attr("stroke", d.role === 'leader' ? '#ffcc00' : d.role === 'finance' ? '#00ff99' : d.role === 'logistics' ? '#007aff' : '#a0b1c5').attr("stroke-width", d.role === 'leader' ? 3 : 2);
                if (d.role === 'leader') { el.append("text").attr("y", -r - 5).attr("x", 0).attr("text-anchor", "middle").attr("class", "fa-solid").style("font-family", "'Font Awesome 6 Free'").style("font-weight", "900").attr("font-size", "24px").attr("fill", "#ffcc00").style("filter", "drop-shadow(0 0 5px #ffcc00)").text("\uf521"); }
            } else {
                let color = "#999", iconCode = "\uf128", iconClass = "fa-solid", fontFamily = "'Font Awesome 6 Free'", fontWeight = "900";
                if (['wallet', 'bank'].includes(d.type)) { color = "#ffcc00"; iconCode = "\uf555"; } else if (['container', 'bol'].includes(d.type)) { color = "#007aff"; iconCode = "\uf468"; } else if (d.type === 'material') { color = "#bd00ff"; iconCode = "\uf1c9"; } else if (d.type === 'traffic') { color = "#ff9500"; iconCode = d.subtype === 'VEHICLE' ? "\uf1b9" : (d.subtype === 'LOCATION' ? "\uf3c5" : (d.subtype === 'DOMAIN' ? "\uf0ac" : "\uf233")); } else if (['social_public', 'social_private'].includes(d.type)) { color = "#d946ef"; if (d.subtype === 'TELEGRAM') { iconCode = "\uf2c6"; iconClass = "fa-brands"; fontFamily = "'Font Awesome 6 Brands'"; fontWeight = "400"; } else if (d.subtype === 'WECHAT') { iconCode = "\uf1d7"; iconClass = "fa-brands"; fontFamily = "'Font Awesome 6 Brands'"; fontWeight = "400"; } else if (d.subtype === 'TWITTER') { iconCode = "\uf099"; iconClass = "fa-brands"; fontFamily = "'Font Awesome 6 Brands'"; fontWeight = "400"; } else if (d.subtype === 'DISCORD') { iconCode = "\uf392"; iconClass = "fa-brands"; fontFamily = "'Font Awesome 6 Brands'"; fontWeight = "400"; } else if (d.subtype === 'WHATSAPP') { iconCode = "\uf232"; iconClass = "fa-brands"; fontFamily = "'Font Awesome 6 Brands'"; fontWeight = "400"; } else if (d.subtype === 'DARKWEB_FORUM') { iconCode = "\uf21b"; iconClass = "fa-solid"; } else if (d.subtype === 'EMAIL') { iconCode = "\uf0e0"; iconClass = "fa-solid"; } else { iconCode = "\uf0a1"; iconClass = "fa-solid"; } }
                el.append("circle").attr("r", r).attr("fill", "#0b1b38").attr("stroke", color).attr("stroke-width", 2).attr("class", `entity-node`); 
                el.append("text").attr("class", iconClass).style("font-family", fontFamily).style("font-weight", fontWeight).attr("font-size", (14 + (d.degree||0)*1.5) + "px").attr("fill", color).attr("dy", (14 + (d.degree||0)*1.5) / 2.5).attr("text-anchor", "middle").text(iconCode);
            }
            const labelText = escapeHTML(d.type === 'user' ? d.name : (d.label || d.value));
            el.append("text").attr("dy", r + 15).attr("text-anchor", "middle").attr("fill", "white").attr("font-size", "11px").attr("font-weight", "bold").attr("class", "label-text bg-black/50 px-2 rounded shadow-md transition-colors").style("text-shadow", "0 1px 2px black").text(labelText);
            if(d.pending_aliases && d.pending_aliases.length > 0) { el.append("circle").attr("cx", r*0.7).attr("cy", -r*0.7).attr("r", 6).attr("fill", "#ff3b30").attr("stroke", "#0b1b38").attr("stroke-width", 1).attr("class", "animate-pulse"); el.append("text").attr("x", r*0.7).attr("y", -r*0.7 + 3).attr("text-anchor", "middle").attr("fill", "white").attr("font-size", "8px").attr("font-weight", "bold").text(d.pending_aliases.length); }
        });
        nodeSelection = nodeEnter.merge(nodeSelection);
        simulation.nodes(fusionData.nodes); simulation.force("link").links(fusionData.links);
        simulation.on("tick", () => {
            nodeSelection.attr("transform", function(d) { const r = d.collisionRadius || 30; d.x = Math.max(r, Math.min(width - r, d.x)); d.y = Math.max(r, Math.min(height - r, d.y)); return `translate(${d.x},${d.y})`; });
            linkSelection.attr("d", d => { const dx = d.target.x - d.source.x, dy = d.target.y - d.source.y; const dr = Math.sqrt(dx * dx + dy * dy) * 2; return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`; });
        });
        updateVisibility();
    }

    function generateInferredLinks() {
        const iocMap = {};
        fusionData.links.forEach(l => {
            const sId = getSafeNodeId(l.source), tId = getSafeNodeId(l.target); const sNode = getSafeNodeObj(l.source), tNode = getSafeNodeObj(l.target);
            if (sNode && sNode.type === 'user' && tNode && tNode.type !== 'user') { if(!iocMap[tId]) iocMap[tId] = []; iocMap[tId].push(sId); }
            if (tNode && tNode.type === 'user' && sNode && sNode.type !== 'user') { if(!iocMap[sId]) iocMap[sId] = []; iocMap[sId].push(tId); }
        });
        const inferredLinks = [];
        Object.keys(iocMap).forEach(iocId => {
            const users = [...new Set(iocMap[iocId])];
            if (users.length > 1) {
                for(let i=0; i<users.length; i++) {
                    for(let j=i+1; j<users.length; j++) {
                        const exists = fusionData.links.find(l => { const lsId = getSafeNodeId(l.source), ltId = getSafeNodeId(l.target); return (lsId === users[i] && ltId === users[j]) || (lsId === users[j] && ltId === users[i]); });
                        if (!exists) {
                            const nowStr = new Date().toISOString().replace('T', ' ').substring(0, 16);
                            inferredLinks.push({ source: users[i], target: users[j], type: 'command', predicate: 'SHARED_IOC', evidence_id: `INF-${users[i]}-${users[j]}-${iocId}`, timestamp: nowStr, method: "智能图推断", hash: "AI_INFERRED", conf: 0.85, evidences: [{ evidence_id: "CAP-AI-" + Math.floor(Math.random()*1000), source_id: "SRC-005", method: "自动推理 (Shared IOC提取)", conf: 0.85, capsule: { vitality_status: "LIVE", capture_time: nowStr, target_url: "internal://ai-engine/infer", snapshot: { type: "JSON", content_hash: "AI_INFERRED" } } }] });
                        }
                    }
                }
            }
        });
        if(inferredLinks.length > 0) fusionData.links.push(...inferredLinks);
    }

    function preprocessData() {
        minTime = null; maxTime = null; currentTimeValue = null; const nodes = fusionData.nodes, links = fusionData.links;
        nodes.forEach(n => { n.degree = 0; n.betweenness = 0; n.domains = new Set(); n.audit_logs = n.audit_logs || []; n.collisionRadius = null; });
        links.forEach(l => { l.audit_logs = l.audit_logs || []; });
        adjOutgoing = {}; nodeLinksMap = {}; nodes.forEach(n => { adjOutgoing[n.id] = []; nodeLinksMap[n.id] = []; });
        links.forEach(l => {
            const sId = getSafeNodeId(l.source), tId = getSafeNodeId(l.target); const sNode = getSafeNodeObj(l.source), tNode = getSafeNodeObj(l.target);
            if (sNode) { sNode.degree++; sNode.domains.add(l.type); } if (tNode) { tNode.degree++; tNode.domains.add(l.type); }
            adjOutgoing[sId].push({ link: l, target: tId }); nodeLinksMap[sId].push(l); nodeLinksMap[tId].push(l);
        });
        Object.keys(nodeLinksMap).forEach(id => nodeLinksMap[id].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()));
        nodes.forEach(n => { n.isBridge = n.domains.size > 1; n.domainList = Array.from(n.domains); });
        nodes.forEach(startNode => {
            let queue = [[startNode.id]], visited = new Set([startNode.id]);
            while(queue.length > 0) {
                let path = queue.shift(), currentId = path[path.length - 1]; let neighbors = adjOutgoing[currentId]?.map(e => e.target) || [];
                neighbors.forEach(nId => { if (!visited.has(nId)) { visited.add(nId); queue.push(path.concat(nId)); for(let i = 1; i < path.length; i++) { let midNode = nodes.find(n => n.id === path[i]); if(midNode) midNode.betweenness++; } } });
            }
        });
        let maxB = nodes.reduce((max, n) => Math.max(max, n.betweenness || 0), 1); nodes.forEach(n => n.betweennessNorm = (n.betweenness / maxB).toFixed(2));
        let times = []; links.forEach(l => { if (l.timestamp) times.push(parseTime(l.timestamp)); }); nodes.forEach(n => { if (n.provenance && n.provenance.time) times.push(parseTime(n.provenance.time)); });
        times = times.filter(t => !isNaN(t)).sort((a,b) => a-b); if(times.length > 0) { minTime = times[0]; maxTime = times[times.length - 1]; currentTimeValue = maxTime; }
    }

    let brushGroup = null; let selectedNodesSet = new Set(); const canvasBrush = d3.brush().on("start brush end", brushed);
    window.toggleBrushMode = () => {
        const btn = document.getElementById('btn-brush-mode'); isBrushMode = !isBrushMode;
        if (isBrushMode) {
            btn.classList.add('border-primary', 'text-primary'); svg.on(".zoom", null); 
            if (!brushGroup) brushGroup = gTopology.append("g").attr("class", "brush z-50");
            brushGroup.call(canvasBrush).style("display", "block"); document.getElementById('timeline-container').classList.add('translate-y-32'); 
        } else {
            btn.classList.remove('border-primary', 'text-primary');
            if (brushGroup) { brushGroup.style("display", "none"); brushGroup.call(canvasBrush.move, null); }
            svg.call(zoomBehavior); document.getElementById('timeline-container').classList.remove('translate-y-32'); window.clearBrushSelection();
        }
    };
    function brushed(event) {
        if (!event.selection) { if (event.type === "end") { selectedNodesSet.clear(); updateBrushVisuals(); } return; }
        const [[x0, y0], [x1, y1]] = event.selection; selectedNodesSet.clear();
        fusionData.nodes.forEach(d => { if (d.x >= x0 && d.x <= x1 && d.y >= y0 && d.y <= y1) selectedNodesSet.add(d.id); });
        if (event.type === "end") updateBrushVisuals();
    }
    function updateBrushVisuals() {
        if(!nodeSelection) return;
        nodeSelection.each(function(d) { d3.select(this).classed('brush-selected', selectedNodesSet.has(d.id)); });
        const fab = document.getElementById('batch-fab');
        if (selectedNodesSet.size > 0) { fab.classList.remove('translate-y-32', 'opacity-0'); document.getElementById('batch-count').innerText = selectedNodesSet.size; } else { fab.classList.add('translate-y-32', 'opacity-0'); }
    }
    window.clearBrushSelection = () => { if(brushGroup) brushGroup.call(canvasBrush.move, null); selectedNodesSet.clear(); updateBrushVisuals(); };

    window.executeSearch = () => {
        const query = document.getElementById('global-search').value.trim().toLowerCase(); if(!query) return;
        const target = fusionData.nodes.find(n => (n.name && n.name.toLowerCase().includes(query)) || (n.value && n.value.toLowerCase().includes(query)) || (n.label && n.label.toLowerCase().includes(query)));
        if(target) {
            focusNode(target); openAnalystPanel(target, 'node');
            const circle = d3.select(`#node-${target.id}`).select("circle.entity-node, circle"); const originalStroke = circle.attr("stroke"); const originalWidth = circle.attr("stroke-width");
            circle.transition().duration(200).style("stroke", "#00f0ff").style("stroke-width", "8px").attr("filter", "drop-shadow(0 0 20px #00f0ff)").transition().duration(2000).ease(d3.easeCircleOut).style("stroke", originalStroke).style("stroke-width", originalWidth).attr("filter", null);
        } else alert("⚠️ 未在当前拓扑界限内检索到匹配的实体对象。");
    };

    function focusNode(d) { if(d.x !== undefined && d.y !== undefined) svg.transition().duration(750).call(zoomBehavior.transform, d3.zoomIdentity.translate(width / 2, height / 2).scale(1.5).translate(-d.x, -d.y)); }

    function updateVisibility() {
        if(isBrushMode) return; const activeLinkSet = new Set(), activeNodeSet = new Set();
        fusionData.links.forEach(l => {
            const linkTime = parseTime(l.timestamp); if (linkTime > currentTimeValue) return;
            let isVisible = true;
            if (currentView === 'finance' && l.type !== 'finance') isVisible = false; if (currentView === 'logistics' && !['logistics', 'material'].includes(l.type)) isVisible = false; if (currentView === 'traffic' && !['traffic'].includes(l.type)) isVisible = false; if (currentView === 'propaganda' && !['referral', 'command'].includes(l.type)) isVisible = false;
            if (!isVisible) return; activeLinkSet.add(l); activeNodeSet.add(getSafeNodeId(l.source)); activeNodeSet.add(getSafeNodeId(l.target));
        });
        linkSelection.transition().duration(400).style("opacity", d => activeLinkSet.has(d) ? (d.conf < 0.7 ? 0.35 : (d.conf || 1)) : 0.05).style("stroke-dasharray", d => (activeLinkSet.has(d) && d.conf < 0.7) ? "4, 8" : null).style("pointer-events", d => activeLinkSet.has(d) ? 'auto' : 'none');
        nodeSelection.transition().duration(400).style("opacity", d => {
            const nodeTime = parseTime(d.provenance?.time); const hasActiveLink = activeNodeSet.has(d.id);
            if (nodeTime > currentTimeValue && !hasActiveLink) return 0;
            if (currentView === 'all') return 1; if (currentView === 'finance' && !(['wallet', 'bank'].includes(d.type) || d.role === 'finance' || d.role === 'leader')) return 0.1; if (currentView === 'logistics' && !(['container', 'bol', 'material'].includes(d.type) || d.role === 'logistics')) return 0.1; if (currentView === 'traffic' && !(['traffic'].includes(d.type) || d.role === 'leader')) return 0.1; if (currentView === 'propaganda' && !(['social_public', 'social_private'].includes(d.type) || d.role === 'member' || d.role === 'leader')) return 0.1;
            return 1;
        }).style("pointer-events", d => { const nodeTime = parseTime(d.provenance?.time); return (nodeTime > currentTimeValue && !activeNodeSet.has(d.id)) ? 'none' : 'auto'; });
    }

    function initTimeline() {
        if (!minTime || !maxTime) { document.getElementById('time-start').innerText = '--'; document.getElementById('time-end').innerText = '--'; document.getElementById('time-current').innerText = '暂无时间轴数据'; return; }
        const slider = document.getElementById('timeline-slider'); slider.min = minTime; slider.max = maxTime; slider.value = maxTime;
        const formatTime = (ts) => { const d = new Date(ts); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`; };
        document.getElementById('time-start').innerText = formatTime(minTime); document.getElementById('time-end').innerText = formatTime(maxTime); document.getElementById('time-current').innerText = formatTime(maxTime);
        slider.addEventListener('input', (e) => { currentTimeValue = parseInt(e.target.value); document.getElementById('time-current').innerText = formatTime(currentTimeValue); updateVisibility(); });
    }

    window.switchView = (view) => {
        document.querySelectorAll('header button[id^="view-"]').forEach(b => { b.className = "px-3 py-1 text-xs rounded hover:bg-white/5 text-textGray hover:text-white transition"; });
        const activeBtn = document.getElementById(`view-${view}`);
        activeBtn.className = "px-4 py-1.5 text-xs rounded bg-primary text-darkBlue font-bold shadow-glow transition-all";
        if (view === 'propaganda') activeBtn.className = "px-4 py-1.5 text-xs rounded bg-propaganda text-white font-bold shadow-glow-propaganda transition-all";
        currentView = view; updateVisibility();
    };

    function populateSidebar() {
        const meta = fusionData.meta;
        document.getElementById('verdict-container').innerHTML = `<div class="flex justify-between items-start mb-2"><div><span class="text-[10px] bg-danger text-white font-bold px-1.5 py-0.5 rounded shadow-glow-danger uppercase">${escapeHTML(meta.level)}级威胁</span><h2 class="text-lg font-bold text-white mt-1 tracking-wide">${escapeHTML(meta.group_id)}</h2><p class="text-[11px] text-white/70 mt-0.5">${escapeHTML(meta.category_label)}</p></div><div class="text-right"><div class="text-3xl font-bold text-white drop-shadow-md">${escapeHTML(meta.risk_score)}</div><div class="text-[9px] text-white/50 uppercase tracking-wider">风险评分</div></div></div><p class="text-[11px] text-gray-200 leading-tight mb-3 border-l-2 border-white/50 pl-2 opacity-90">${escapeHTML(meta.description)}</p>`;
        let memCount = 0, finCount = 0, matCount = 0, trafCount = 0, propCount = 0; const memberList = document.getElementById('member-list'); const lists = { finance: document.getElementById('entity-list-finance'), material: document.getElementById('entity-list-material'), traffic: document.getElementById('entity-list-traffic'), propaganda: document.getElementById('entity-list-propaganda') };
        memberList.innerHTML=''; Object.values(lists).forEach(l => l.innerHTML = '');
        fusionData.nodes.forEach(n => {
            if (n.type === 'user') {
                memCount++; const div = document.createElement('div'); div.className = "p-3 rounded bg-white/5 border border-white/10 hover:border-primary/50 transition group";
                let userLinksHtml = ''; let userLinks = nodeLinksMap[n.id] || []; let recentLinks = userLinks.slice(-5); 
                if (recentLinks.length > 0) {
                    userLinksHtml += `<div class="mt-3 space-y-1.5 border-t border-white/10 pt-2 h-[80px] overflow-y-auto custom-scrollbar pr-1">`;
                    recentLinks.forEach(l => {
                        let isSource = getSafeNodeId(l.source) === n.id; let otherNodeId = isSource ? getSafeNodeId(l.target) : getSafeNodeId(l.source); let otherNode = fusionData.nodes.find(x => x.id === otherNodeId);
                        let otherName = otherNode ? (otherNode.name || otherNode.label || otherNode.value) : '未知目标'; let predicateZh = predicateMap[l.predicate]?.zh || l.predicate;
                        let actionText = isSource ? `<span class="text-primary font-bold">${escapeHTML(predicateZh)}</span> <i class="fa-solid fa-arrow-right text-[8px] text-gray-500 mx-1"></i> <span class="text-gray-300 truncate max-w-[100px] inline-block align-bottom" title="${escapeHTML(otherName)}">${escapeHTML(otherName)}</span>` : `<i class="fa-solid fa-arrow-left text-[8px] text-gray-500 mr-1"></i>被 <span class="text-gray-300 truncate max-w-[60px] inline-block align-bottom" title="${escapeHTML(otherName)}">${escapeHTML(otherName)}</span> <span class="text-warning font-bold">${escapeHTML(predicateZh)}</span>`;
                        userLinksHtml += `<div class="text-[10px] text-gray-400 flex items-start cursor-pointer hover:bg-black/30 p-1 rounded" onclick="event.stopPropagation(); window.findAndShow('${l.evidence_id}', 'link')"><span class="text-gray-500 shrink-0 font-mono mr-1.5">[${(l.timestamp||'').split(' ')[0].substring(5)}]</span><span class="leading-tight flex-1">${actionText}</span></div>`;
                    });
                    userLinksHtml += `</div>`;
                } else { userLinksHtml = `<div class="text-[9px] text-gray-500 mt-2 italic border-t border-white/10 pt-2 text-center">暂无固化行为链路</div>`; }
                div.innerHTML = `<div class="flex items-center gap-3 cursor-pointer" onclick="window.findAndShow('${n.id}', 'node')"><img src="${escapeHTML(n.avatar)}" class="w-10 h-10 rounded-full border border-gray-500 group-hover:border-primary transition shrink-0"><div class="flex-1 min-w-0"><div class="flex justify-between items-baseline mb-0.5"><span class="text-sm font-bold text-white truncate">${escapeHTML(n.name)}</span><span class="text-[9px] px-1.5 py-0.5 rounded font-bold border ${n.risk==='CRITICAL'?'bg-danger/10 text-danger border-danger/30':'bg-warning/10 text-warning border-warning/30'}">${escapeHTML(n.risk)}</span></div><div class="text-[10px] text-gray-400 truncate"><i class="fa-solid fa-tags text-[8px] mr-1 opacity-50"></i>${escapeHTML((n.tags||[]).join(', '))}</div></div></div>${userLinksHtml}`; memberList.appendChild(div);
            } 
            else if (['wallet', 'bank'].includes(n.type)) { finCount++; lists.finance.innerHTML += createEntityItem(n, 'warning'); } else if (['material', 'container', 'bol'].includes(n.type)) { matCount++; lists.material.innerHTML += createEntityItem(n, 'material'); } else if (['traffic'].includes(n.type)) { trafCount++; lists.traffic.innerHTML += createEntityItem(n, 'traffic'); } else if (['social_public', 'social_private'].includes(n.type)) { propCount++; lists.propaganda.innerHTML += createEntityItem(n, 'propaganda'); }
        });
        document.getElementById('member-count').innerText = memCount; document.getElementById('finance-count').innerText = finCount; document.getElementById('material-count').innerText = matCount; document.getElementById('traffic-count').innerText = trafCount; document.getElementById('propaganda-count').innerText = propCount;
    }

    function createEntityItem(node, colorClass) {
        let iconClass = 'fa-solid fa-circle';
        if (['wallet', 'bank'].includes(node.type)) { iconClass = 'fa-solid fa-coins'; } else if (['container', 'bol'].includes(node.type)) { iconClass = 'fa-solid fa-box'; } else if (node.type === 'material') { iconClass = 'fa-solid fa-file-code'; } else if (node.type === 'traffic') { iconClass = node.subtype === 'VEHICLE' ? 'fa-solid fa-car' : (node.subtype === 'LOCATION' ? 'fa-solid fa-location-dot' : 'fa-solid fa-server'); } else if (['social_public', 'social_private'].includes(node.type)) { if (node.subtype === 'TELEGRAM') iconClass = 'fa-brands fa-telegram'; else if (node.subtype === 'WECHAT') iconClass = 'fa-brands fa-weixin'; else if (node.subtype === 'TWITTER') iconClass = 'fa-brands fa-twitter'; else if (node.subtype === 'DISCORD') iconClass = 'fa-brands fa-discord'; else if (node.subtype === 'WHATSAPP') iconClass = 'fa-brands fa-whatsapp'; else if (node.subtype === 'DARKWEB_FORUM') iconClass = 'fa-solid fa-user-ninja'; else if (node.subtype === 'EMAIL') iconClass = 'fa-solid fa-envelope'; else iconClass = 'fa-solid fa-bullhorn'; }
        let bridgeHtml = node.isBridge ? `<i class="fa-solid fa-link text-white/50 text-[8px] ml-1" title="跨域枢纽"></i>` : ''; return `<div class="flex items-center justify-between text-xs font-mono p-1.5 bg-${colorClass}/10 border border-${colorClass}/20 rounded text-${colorClass} hover:bg-${colorClass}/20 cursor-pointer transition" onclick="window.findAndShow('${node.id}', 'node')"><span class="truncate w-32"><i class="${iconClass} mr-1.5 opacity-70"></i>${escapeHTML(node.value)}</span><span class="text-[9px] bg-black/30 px-1 rounded ml-2 opacity-60">${escapeHTML(node.subtype || 'UNKN')}${bridgeHtml}</span></div>`;
    }

    window.findAndShow = (id, type='node') => { 
        if(isBrushMode) return;
        if(type === 'node') { const data = fusionData.nodes.find(n => n.id === id); if (data) { openAnalystPanel(data, 'node'); focusNode(data); } } 
        else { const data = fusionData.links.find(l => l.evidence_id === id); if (data) { const sN = getSafeNodeObj(data.source); if(sN) focusNode(sN); openAnalystPanel(data, 'link'); } }
    }

    function generateAuditHTML(logs) { 
        if (!logs || logs.length === 0) return '<div class="text-[10px] text-gray-500 italic">暂无审计记录</div>'; 
        return logs.map(log => `<div class="flex gap-2 mb-3 items-start border-l-2 border-primary/30 pl-2 ml-1 relative"><div class="absolute w-2 h-2 rounded-full bg-primary -left-[5px] top-1 shadow-glow"></div><div class="w-full"><div class="flex justify-between items-center text-[10px]"><span class="text-primary font-bold">${escapeHTML(log.user)}</span> <span class="text-gray-500 font-mono scale-90">${escapeHTML(log.time)}</span></div><div class="text-[11px] text-white mt-0.5 bg-black/40 p-1.5 rounded border border-white/5">${escapeHTML(log.detail)}</div>${log.reason && log.reason !== '无备注' ? `<div class="text-[10px] text-warning mt-1 italic"><i class="fa-solid fa-quote-left mr-1 opacity-50"></i>${escapeHTML(log.reason)}</div>` : ''}</div></div>`).join(''); 
    }

    window.switchNodeTab = (tabId) => { ['schema', 'mastering', 'cluster'].forEach(t => { const btn = document.getElementById(`tab-btn-${t}`); const pane = document.getElementById(`pane-${t}`); if(btn && pane) { btn.classList.toggle('active', t === tabId); pane.classList.toggle('hidden', t !== tabId); } }); };

    window.handleAliasAction = (masterId, aliasId, action) => {
        const masterNodeIndex = fusionData.nodes.findIndex(n => n.id === masterId), aliasNodeIndex = fusionData.nodes.findIndex(n => n.id === aliasId); if (masterNodeIndex === -1 || aliasNodeIndex === -1) return alert('实体索引错误或已在另一进程中被合并。'); const masterNode = fusionData.nodes[masterNodeIndex], aliasNode = fusionData.nodes[aliasNodeIndex]; const timeStr = new Date().toLocaleString();
        if (action === 'merge') {
            fusionData.links.forEach(l => { let sId = getSafeNodeId(l.source); let tId = getSafeNodeId(l.target); if (sId === aliasId) l.source = masterId; if (tId === aliasId) l.target = masterId; });
            if(aliasNode.tags) { masterNode.tags = [...new Set([...(masterNode.tags||[]), ...aliasNode.tags])]; } fusionData.nodes.splice(aliasNodeIndex, 1); masterNode.pending_aliases = masterNode.pending_aliases.filter(a => a.target_id !== aliasId); masterNode.audit_logs.push({ time: timeStr, user: "分析师 (04291)", action: "图谱合并", detail: `接受引擎裁决，将实体 [${aliasNode.name||aliasNode.label}] 物理吸收。`, reason: "特征完全吻合" }); alert('✅ 合并成功！节点及其历史边已发生物理吸收。'); initGraph(); openAnalystPanel(masterNode, 'node'); window.switchNodeTab('mastering');
        } else if (action === 'reject') { masterNode.pending_aliases = masterNode.pending_aliases.filter(a => a.target_id !== aliasId); masterNode.audit_logs.push({ time: timeStr, user: "分析师 (04291)", action: "驳回推荐", detail: `拒绝引擎推荐，未将 [${aliasNode.name||aliasNode.label}] 视为主实体的别名。`, reason: "缺乏关键佐证" }); alert('🚫 已驳回该合并推荐，引擎将不再提示。'); openAnalystPanel(masterNode, 'node'); window.switchNodeTab('mastering'); initGraph(); }
    };

    function openAnalystPanel(data, itemType) {
        currentSelectedData = data; currentItemType = itemType; document.getElementById('details-panel').classList.remove('translate-x-full');
        const timelineHtml = generateNodeTimeline(data);
        let headerHtml = `<div class="px-5 py-4 border-b border-white/10 bg-black/20 flex justify-between items-center"><div class="flex items-center gap-2"><span class="text-primary"><i class="fa-solid fa-shield-halved"></i></span><h2 class="text-sm font-bold text-white tracking-wider">Schema 属性与情报审查</h2></div><button onclick="document.getElementById('details-panel').classList.add('translate-x-full')" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button></div>`;
        let bodyHtml = '';

        if (itemType === 'node') {
            const isUser = data.type === 'user'; const prov = data.provenance || { source: 'Engine 自动提取', time: new Date().toISOString().substring(0, 16).replace('T', ' ') };
            let fallbackStage = 'RECON'; let fallbackCorridor = 'OSINT_GENERAL';
            if (['social_public', 'social_private'].includes(data.type)) { fallbackStage = 'PROMOTION'; fallbackCorridor = 'SOCIAL_GRAPH_API'; } else if (['wallet', 'bank'].includes(data.type)) { fallbackStage = 'TRANSACTION'; fallbackCorridor = 'BLOCKCHAIN_LEDGER'; } else if (['material', 'container', 'bol'].includes(data.type)) { fallbackStage = 'DELIVERY'; fallbackCorridor = 'CUSTOMS_EDIS'; } else if (data.type === 'traffic') { fallbackStage = data.subtype === 'LOCATION' ? 'EXECUTION' : 'RECON'; fallbackCorridor = 'SIGINT_TRAFFIC'; }
            const telemetry = prov.telemetry || { funnel_stage: fallbackStage, route_corridor: fallbackCorridor, query_family: 'HEURISTIC_INFER' };
            let riskColor = data.risk === 'CRITICAL' ? 'text-danger' : data.risk === 'HIGH' ? 'text-orange-500' : data.risk === 'MEDIUM' ? 'text-warning' : 'text-primary'; let pendingCount = (data.pending_aliases && data.pending_aliases.length) ? data.pending_aliases.length : 0; let badgeHtml = pendingCount > 0 ? `<span class="bg-danger text-white px-1.5 rounded-full text-[9px] animate-pulse ml-1">${pendingCount}</span>` : ''; let hasCluster = data.content_cluster && data.content_cluster.length > 0; let clusterTabHtml = hasCluster ? `<button id="tab-btn-cluster" class="tab-btn flex-1 flex justify-center items-center gap-1" onclick="window.switchNodeTab('cluster')"><i class="fa-solid fa-share-nodes"></i> 传播溯源</button>` : '';
            headerHtml += `<div class="flex border-b border-white/10 bg-black/40"><button id="tab-btn-schema" class="tab-btn active flex-1" onclick="window.switchNodeTab('schema')">底层图谱属性</button><button id="tab-btn-mastering" class="tab-btn flex-1" onclick="window.switchNodeTab('mastering')">主数据(同一性)${badgeHtml}</button>${clusterTabHtml}</div>`;
            let funnelStages = ['RECON', 'PROMOTION', 'TRANSACTION', 'DELIVERY', 'EXECUTION']; let funnelLabels = ['侦察/备料', '引流宣发', '资金交易', '物流交付', '行动执行']; let activeIndex = funnelStages.indexOf(telemetry.funnel_stage); if(activeIndex === -1 && telemetry.funnel_stage !== 'UNKNOWN') activeIndex = 0; 
            let stepsHtml = funnelStages.map((stage, idx) => { let isActive = idx === activeIndex; let isPast = idx < activeIndex; let colorClass = isActive ? 'bg-primary border-primary shadow-[0_0_8px_rgba(0,240,255,0.8)] text-darkBlue' : (isPast ? 'bg-primary/50 border-primary/50 text-white' : 'bg-gray-800 border-gray-600 text-gray-500'); let textClass = isActive ? 'text-primary font-bold' : (isPast ? 'text-gray-300' : 'text-gray-600'); return `<div class="flex flex-col items-center z-10 relative"><div class="w-5 h-5 rounded-full border text-[9px] flex items-center justify-center transition-all ${colorClass}">${isPast ? '<i class="fa-solid fa-check"></i>' : (isActive ? '<i class="fa-solid fa-crosshairs fa-spin"></i>' : idx+1)}</div><div class="text-[9px] mt-1.5 text-center whitespace-nowrap ${textClass}">${funnelLabels[idx]}</div></div>`; }).join('');
            let telemetryHtml = `<div class="mt-4 bg-black/40 border border-primary/20 p-3 rounded-lg relative overflow-hidden"><div class="absolute top-0 left-0 w-1 h-full bg-primary/80 shadow-[0_0_10px_#00f0ff]"></div><h4 class="text-[10px] text-primary font-bold mb-3 uppercase flex items-center gap-1.5"><i class="fa-solid fa-filter"></i> 遥测与漏斗归因 (Telemetry)</h4><div class="flex items-center justify-between mb-4 relative px-2"><div class="absolute left-4 right-4 top-[10px] h-[2px] bg-gray-700 z-0"></div><div class="absolute left-4 top-[10px] h-[2px] bg-primary transition-all duration-500 z-0 shadow-[0_0_5px_#00f0ff]" style="width: ${activeIndex >= 0 ? (activeIndex / (funnelStages.length - 1)) * 100 : 0}%"></div>${stepsHtml}</div><div class="grid grid-cols-2 gap-3 text-[10px] bg-black/50 p-2.5 rounded border border-white/5 mt-2"><div class="flex flex-col"><span class="text-gray-500 mb-0.5"><i class="fa-solid fa-route mr-1"></i> 路由通道 (Corridor)</span> <span class="text-white font-mono bg-white/10 px-1.5 py-0.5 rounded w-fit truncate" title="${escapeHTML(telemetry.route_corridor)}">${escapeHTML(telemetry.route_corridor)}</span></div><div class="flex flex-col"><span class="text-gray-500 mb-0.5"><i class="fa-solid fa-magnifying-glass-chart mr-1"></i> 探针族 (Query Family)</span> <span class="text-white font-mono bg-white/10 px-1.5 py-0.5 rounded w-fit truncate" title="${escapeHTML(telemetry.query_family)}">${escapeHTML(telemetry.query_family)}</span></div></div></div>`;
            let schemaHtml = `<div id="pane-schema" class="flex-1 overflow-y-auto p-5 space-y-6 custom-scrollbar"><div class="space-y-3"><label class="text-[10px] text-gray-400 uppercase font-bold">主标识 (锁定)</label><input type="text" value="${escapeHTML(data.name || data.value)}" class="analyst-input text-lg font-bold" readonly><div class="grid grid-cols-2 gap-4"><div><label class="text-[10px] text-gray-400 uppercase font-bold">威胁等级</label><select id="input-risk" class="analyst-input ${riskColor} font-bold" onchange="this.className = 'analyst-input font-bold ' + (this.value==='CRITICAL'?'text-danger':this.value==='HIGH'?'text-orange-500':'text-warning')"><option value="CRITICAL" ${data.risk==='CRITICAL'?'selected':''}>极高危 (CRITICAL)</option><option value="HIGH" ${data.risk==='HIGH'?'selected':''}>高危 (HIGH)</option><option value="MEDIUM" ${data.risk==='MEDIUM'?'selected':''}>中危 (MEDIUM)</option><option value="LOW" ${data.risk==='LOW'?'selected':''}>低危 (LOW)</option></select></div><div><label class="text-[10px] text-gray-400 uppercase font-bold">实体状态</label><select id="input-status" class="analyst-input text-white font-bold"><option value="ACTIVE" ${data.status==='ACTIVE'?'selected':''}>活跃 (ACTIVE)</option><option value="MONITORED" ${data.status==='MONITORED'?'selected':''}>布控中 (MONITORED)</option><option value="ARRESTED" ${data.status==='ARRESTED'?'selected':''}>封禁/落网 (ARRESTED)</option><option value="UNKNOWN" ${!data.status || data.status==='UNKNOWN'?'selected':''}>未知 (UNKNOWN)</option></select></div></div><div class="grid grid-cols-2 gap-4"><div><label class="text-[10px] text-gray-400 uppercase font-bold">桥接中心性分析</label><div class="px-2 py-1 border border-white/10 rounded text-xs mt-1 font-bold flex justify-between ${data.isBridge ? 'bg-warning/10 text-warning border-warning/50' : 'bg-white/5 text-primary'}"><span>${data.isBridge ? '<i class="fa-solid fa-network-wired mr-1"></i> 跨域枢纽' : '<i class="fa-solid fa-share-nodes mr-1"></i> 普通节点'}</span><span>${data.betweennessNorm || 0}</span></div></div></div><div class="grid grid-cols-2 gap-4 mt-1"><div><label class="text-[10px] text-gray-400 uppercase font-bold"><i class="fa-solid fa-tags mr-1"></i>业务标签 (Tags,逗号分隔)</label><input type="text" id="input-tags" value="${escapeHTML((data.tags||[]).join(', '))}" class="analyst-input text-xs mt-1"></div><div><label class="text-[10px] text-gray-400 uppercase font-bold"><i class="fa-solid fa-user-secret mr-1"></i>已知别名 (Aliases)</label><input type="text" id="input-aliases" value="${escapeHTML((data.known_aliases||[]).join(', '))}" class="analyst-input text-xs mt-1"></div></div></div>${!isUser ? `<div class="h-px bg-white/10 w-full"></div><div><div class="flex justify-between items-center mb-3"><h3 class="text-xs font-bold text-primary"><i class="fa-solid fa-globe mr-1"></i> 初始情报源</h3><div class="flex gap-1"><span class="grade-badge ${prov.reliability ? 'grade-'+prov.reliability : 'bg-gray-600'}" title="来源可靠度级别">评估 ${prov.reliability || 'B'}</span></div></div><div class="bg-black/30 border border-white/10 rounded p-3 space-y-2 text-xs"><div class="grid grid-cols-[80px_1fr] gap-2"><span class="text-gray-500">证据源头:</span><span class="text-white">${escapeHTML(prov.source || 'Engine 提取')}</span></div><div class="grid grid-cols-[80px_1fr] gap-2"><span class="text-gray-500">发现时间:</span><span class="text-gray-300 font-mono">${escapeHTML(prov.time || 'N/A')}</span></div></div>${telemetryHtml}</div>` : `<div class="bg-yellow-500/10 border border-yellow-500/20 p-3 rounded text-xs text-yellow-200"><div class="flex items-center gap-2 mb-2"><img src="${escapeHTML(data.avatar)}" class="w-8 h-8 rounded-full border border-yellow-500/50"><div><div class="font-bold">HUMINT 目标人物画像</div><div class="text-[10px] opacity-70">综合风险分: ${data.score}</div></div></div><i class="fa-solid fa-triangle-exclamation mr-1"></i> <strong>法庭说明:</strong> 嫌疑人实体节点需配合关联边才具有法律效力。</div>`}<div class="bg-black/30 border border-white/10 rounded p-3 mt-4"><h3 class="text-xs font-bold text-primary mb-3"><i class="fa-solid fa-timeline mr-1"></i> 涉案时序流水线</h3><div class="space-y-1 overflow-y-auto max-h-40 custom-scrollbar pr-1">${timelineHtml}</div></div><div class="mt-4"><h3 class="text-xs font-bold text-primary mb-2"><i class="fa-solid fa-pen-nib mr-1"></i> 实体研判批注</h3><textarea id="analyst-note-input" rows="2" class="analyst-input text-xs leading-relaxed text-gray-300" placeholder="说明修改理由..."></textarea></div><div class="bg-black/30 border border-white/10 rounded p-3 mt-4"><h3 class="text-xs font-bold text-gray-400 mb-3"><i class="fa-solid fa-clock-rotate-left mr-1"></i> 实体审计日志</h3><div id="audit-log-container" class="space-y-1 overflow-y-auto max-h-32 custom-scrollbar">${generateAuditHTML(data.audit_logs)}</div></div></div>`;
            let masteringHtml = `<div id="pane-mastering" class="flex-1 overflow-y-auto p-5 space-y-6 custom-scrollbar hidden">`;
            if (pendingCount === 0) { masteringHtml += `<div class="flex flex-col items-center justify-center h-40 text-gray-500"><i class="fa-solid fa-circle-check text-4xl mb-3 text-green-500/50"></i><p class="text-xs">该实体的数据当前非常干净，暂无引擎推荐的融合项。</p></div>`; } else {
                masteringHtml += `<div class="bg-blue-900/20 border border-blue-500/30 p-3 rounded text-xs text-blue-200 mb-4"><i class="fa-solid fa-robot mr-1"></i> <strong>引擎建议：</strong> 检测到以下图谱节点可能为当前实体 [${escapeHTML(data.name||data.value)}] 的别名或平行资产。</div>`;
                data.pending_aliases.forEach(alias => { let cColor = alias.conf >= 0.8 ? 'text-green-400 border-green-500/50 bg-green-500/10' : 'text-warning border-warning/50 bg-warning/10'; masteringHtml += `<div class="bg-black/40 border border-white/10 p-3 rounded relative hover:border-primary/50 transition"><div class="flex justify-between items-center mb-2"><span class="text-sm font-bold text-white cursor-pointer hover:underline" onclick="focusNode(fusionData.nodes.find(n=>n.id==='${alias.target_id}'))"><i class="fa-solid fa-crosshairs text-primary mr-1 text-[10px]"></i> ${escapeHTML(alias.target_name)}</span><span class="text-[9px] px-1.5 py-0.5 rounded border font-mono ${cColor}">置信度 ${alias.conf}</span></div><p class="text-[11px] text-gray-400 leading-tight mb-3 pl-2 border-l-2 border-primary/50">${escapeHTML(alias.reason)}</p><div class="flex gap-2 justify-end pt-2 border-t border-white/10"><button class="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-[10px] rounded transition" onclick="window.handleAliasAction('${data.id}', '${alias.target_id}', 'reject')"><i class="fa-solid fa-xmark mr-1 text-red-400"></i> 驳回推荐</button><button class="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white text-[10px] rounded font-bold shadow-glow transition" onclick="window.handleAliasAction('${data.id}', '${alias.target_id}', 'merge')"><i class="fa-solid fa-link"></i> 确认物理合并</button></div></div>`; });
            } masteringHtml += `</div>`;
            let clusterHtml = `<div id="pane-cluster" class="flex-1 overflow-y-auto p-5 custom-scrollbar hidden relative">`;
            if (hasCluster) {
                clusterHtml += `<div class="bg-propaganda/10 border border-propaganda/30 p-3 rounded text-xs text-purple-200 mb-6 flex items-start gap-2"><i class="fa-solid fa-circle-nodes mt-0.5"></i><div><strong>跨域传播分析：</strong>引擎检测到关于此实体的同源情报曾在多个外部平台分发。已还原传播路径与时间线。</div></div><div class="relative pl-6"><div class="cluster-line"></div>`; 
                data.content_cluster.forEach((cc, idx) => { let isFirst = idx === 0; let iconColor = isFirst ? 'text-red-500' : 'text-primary'; let bgIcon = isFirst ? 'bg-red-500/20 border-red-500/50' : 'bg-primary/20 border-primary/50'; clusterHtml += `<div class="mb-6 cluster-node"><div class="absolute -left-[30px] w-6 h-6 rounded-full ${bgIcon} border flex items-center justify-center ${iconColor} text-[10px] shadow-lg"><i class="fa-solid ${isFirst ? 'fa-fire' : 'fa-arrow-down-short-wide'}"></i></div><div class="bg-black/50 border border-white/10 rounded p-3 hover:border-primary/50 transition"><div class="flex justify-between items-baseline mb-1"><span class="text-xs font-bold text-white">${escapeHTML(cc.source)}</span><span class="text-[10px] text-gray-500 font-mono">${escapeHTML(cc.time)}</span></div><div class="text-[11px] text-gray-300 mb-2 leading-tight">${escapeHTML(cc.desc)}</div><div class="flex justify-between items-center pt-2 border-t border-white/5"><span class="text-[9px] text-gray-500 font-mono" title="防篡改完整性校验">Hash: ${escapeHTML(cc.hash)}</span>${isFirst ? '<span class="text-[9px] bg-red-500 text-white px-1 rounded">源头发源地 (Patient Zero)</span>' : ''}</div></div></div>`; }); clusterHtml += `</div>`;
            } clusterHtml += `</div>`;
            bodyHtml = schemaHtml + masteringHtml + clusterHtml + `<div class="p-4 border-t border-white/10 bg-black/40 flex gap-3"><button id="save-btn" class="flex-1 bg-primary/20 hover:bg-primary/30 text-primary border border-primary/40 py-2 rounded text-xs font-bold transition flex justify-center items-center" onclick="window.saveChanges()"><i class="fa-solid fa-floppy-disk mr-1"></i> 提交批注并审计</button></div>`;

        } else {
            const sN = getSafeNodeObj(data.source); const tN = getSafeNodeObj(data.target); const sourceName = sN.name || sN.value || sN.label; const targetName = tN.name || tN.value || tN.label;
            let predicateOptions = Object.keys(predicateMap).map(p => `<option value="${p}" ${data.predicate === p ? 'selected' : ''}>${escapeHTML(predicateMap[p].zh)} (${p})</option>`).join('');
            let snippetHtml = '';
            if (data.raw_content_preview) {
                let highlightedText = escapeHTML(data.raw_content_preview);
                if (data.matched_terms) { Object.values(data.matched_terms).flat().forEach(term => { const regex = new RegExp(escapeHTML(term), 'gi'); highlightedText = highlightedText.replace(regex, `<span class="bg-danger/30 text-danger font-bold px-0.5 rounded border border-danger/50">$&</span>`); }); }
                snippetHtml = `<div class="mt-4 bg-black/40 border border-primary/30 p-3 rounded-lg relative overflow-hidden shadow-glow"><div class="absolute top-0 left-0 w-1 h-full bg-primary"></div><h3 class="text-[10px] font-bold text-primary mb-2 flex items-center gap-2"><i class="fa-solid fa-quote-left"></i> 命中摘要 & 黑话 (Match Snippet)</h3><div class="text-xs text-gray-300 leading-relaxed font-mono whitespace-pre-wrap">${highlightedText}</div></div>`;
            }
            let evidenceListHtml = ''; let finalConfSliderId = 'final-conf-slider';
            if (data.evidences && data.evidences.length > 0) {
                let conflictBanner = data.is_conflicted ? `<div class="bg-red-500/20 border border-red-500/50 text-red-400 p-2 rounded text-xs mb-3 flex items-start gap-2 shadow-glow-danger"><i class="fa-solid fa-triangle-exclamation mt-0.5"></i> <span><strong>多源情报冲突：</strong>请勾选采纳的证据，并调整最终置信度。</span></div>` : '';
                let listItems = data.evidences.map(ev => {
                    let sourceInfo = fusionData.sourceRegistry[ev.source_id] || { name: '提取器/系统', reliability: 'C', type: 'SYS', frequency: 'N/A', desc: '系统内建或临时引入的数据源。' }; let cap = ev.capsule || {}; let vStatus = cap.vitality_status || 'DEGRADED'; let vColor = vStatus === 'LIVE' ? 'text-green-500' : (vStatus === 'ARCHIVED' ? 'text-yellow-500' : 'text-red-500'); let vLabel = vStatus === 'LIVE' ? '可复现' : (vStatus === 'ARCHIVED' ? '已归档' : '降级/残缺');
                    return `<div class="bg-black/40 border border-white/10 rounded overflow-hidden mb-3 relative hover:border-primary/30 transition"><div class="flex justify-between items-center bg-white/5 px-2 py-1 border-b border-white/10"><div class="flex items-center gap-2 group relative cursor-help"><span class="grade-badge ${sourceInfo.reliability ? 'grade-'+sourceInfo.reliability : 'bg-gray-600'}">源评级 ${sourceInfo.reliability}</span><span class="text-xs text-gray-300 font-bold truncate max-w-[120px]">${escapeHTML(sourceInfo.name)}</span><div class="absolute left-0 top-6 w-48 bg-gray-900 border border-gray-600 p-2 rounded shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 text-[10px] text-gray-300"><div class="font-bold text-white border-b border-gray-700 pb-1 mb-1">${escapeHTML(sourceInfo.type)}</div><div>更新频次: ${escapeHTML(sourceInfo.frequency)}</div><div class="mt-1 italic opacity-80">${escapeHTML(sourceInfo.desc)}</div></div></div><div class="flex items-center gap-2"><label class="text-[10px] text-gray-400 flex items-center gap-1"><input type="checkbox" class="evidence-checkbox accent-blue-500" data-ev-id="${ev.evidence_id}" value="accept" checked> 采纳</label><span class="text-[10px] px-1.5 py-0.5 rounded border ${ev.conf >= 0.8 ? 'text-green-400 border-green-500/30 bg-green-500/10' : (ev.conf >= 0.5 ? 'text-warning border-warning/30 bg-warning/10' : 'text-gray-400 border-gray-600 bg-gray-800')}">置信度 ${ev.conf}</span></div></div><div class="p-2 space-y-1.5"><div class="flex justify-between items-center text-[10px]"><div class="flex items-center gap-1.5 ${vColor} font-bold"><span class="status-dot status-${vStatus}"></span>${vLabel}</div><div class="text-gray-500 font-mono">${escapeHTML(cap.capture_time || '未知时间')}</div></div><div class="text-[10px] text-gray-400 grid grid-cols-[50px_1fr] gap-x-2 gap-y-1 bg-black/50 p-1.5 rounded border border-white/5"><span>目标URL:</span><span class="text-blue-400 truncate cursor-pointer hover:underline" title="${escapeHTML(cap.target_url)}">${escapeHTML(cap.target_url || 'N/A')}</span><span>提取节点:</span><span class="truncate">${escapeHTML(cap.capture_node || 'N/A')}</span><span>Hash:</span><span class="font-mono text-gray-500 truncate" title="${escapeHTML(cap.snapshot?.content_hash)}">${escapeHTML(cap.snapshot?.content_hash || 'N/A')}</span></div>${ev.note ? `<div class="mt-1 text-[10px] text-danger bg-danger/10 p-1.5 rounded border border-danger/30 leading-tight"><i class="fa-solid fa-circle-info mr-1"></i>${escapeHTML(ev.note)}</div>` : ''}<div class="pt-1 flex justify-end"> <button class="px-2 py-1 bg-primary/20 hover:bg-primary/40 text-primary text-[10px] rounded border border-primary/30 transition flex items-center gap-1" onclick="window.showRawEvidence('${ev.evidence_id}', '${getSafeNodeId(data.source)}')"><i class="fa-solid fa-file-shield"></i> 调阅原始快照与智能分析</button></div></div></div>`;
                }).join('');
                evidenceListHtml = `<div class="mt-4"><h3 class="text-xs font-bold text-gray-400 mb-3 flex items-center gap-2"><i class="fa-solid fa-layer-group text-primary"></i> 支撑证据群 / Capsule包 (${data.evidences.length})</h3>${conflictBanner}<div class="max-h-72 overflow-y-auto custom-scrollbar pr-1">${listItems}</div></div><div class="mt-3 flex items-center gap-2"><span class="text-xs text-gray-400">最终置信度:</span><input type="range" id="${finalConfSliderId}" min="0.1" max="1.0" step="0.05" value="${data.conf}" class="w-full accent-blue-500"> <span id="final-conf-display" class="text-primary text-sm font-bold">${data.conf}</span></div><div class="h-px bg-white/10 w-full my-4"></div>`;
            } else { evidenceListHtml = `<div class="mt-4 bg-black/30 p-3 rounded border border-white/10 text-xs text-gray-400 italic">该链路无额外的底层溯源证据包，系单一来源或人工直录。</div><div class="h-px bg-white/10 w-full my-4"></div>`; }

            bodyHtml = `<div class="p-5 overflow-y-auto custom-scrollbar flex-1 space-y-4"><div class="flex flex-col gap-2 bg-black/30 p-3 rounded border border-white/10"><div class="flex justify-between items-center text-xs"><span class="text-gray-400">研判固化时间:</span><span class="text-white font-mono bg-white/10 px-2 py-0.5 rounded">${escapeHTML(data.timestamp || 'N/A')}</span></div><div class="flex justify-between items-center mt-2"><span class="text-sm font-bold text-white truncate w-[40%] text-center border-b border-gray-600 pb-1" title="${escapeHTML(sourceName)}">${escapeHTML(sourceName)}</span><div class="flex flex-col items-center w-[20%] text-primary"><i class="fa-solid fa-arrow-right"></i></div><span class="text-sm font-bold text-white truncate w-[40%] text-center border-b border-gray-600 pb-1" title="${escapeHTML(targetName)}">${escapeHTML(targetName)}</span></div></div><div class="grid grid-cols-2 gap-4"><div class="space-y-1"><label class="text-[10px] text-gray-400 uppercase font-bold">关系本体 (Predicate)</label><select id="input-predicate" class="analyst-input text-xs font-bold text-primary">${predicateOptions}</select></div><div class="space-y-1"><label class="text-[10px] text-gray-400 uppercase font-bold">综合研判置信度</label><input id="input-conf" type="number" step="0.1" max="1.0" min="0" value="${data.conf || 0.8}" class="analyst-input ${data.conf < 0.7 ? 'text-danger' : 'text-primary'}" readonly></div></div>${snippetHtml}${evidenceListHtml}<div class="space-y-1"><label class="text-[10px] text-primary font-bold"><i class="fa-solid fa-pen-nib mr-1"></i> 裁决调整说明 / 理由</label><textarea id="analyst-note-input" rows="2" class="analyst-input text-xs leading-relaxed text-gray-300" placeholder="说明为何采纳/修改该边..."></textarea></div><div class="bg-black/30 border border-white/10 rounded p-3 mt-4"><h3 class="text-xs font-bold text-gray-400 mb-3"><i class="fa-solid fa-clock-rotate-left mr-1"></i> 链路裁决审计日志</h3><div id="audit-log-container" class="space-y-1 overflow-y-auto max-h-32 custom-scrollbar">${generateAuditHTML(data.audit_logs)}</div></div></div><div class="p-4 border-t border-white/10 bg-black/40 flex gap-3"><button id="save-btn" class="w-full bg-primary/20 hover:bg-primary/30 text-primary border border-primary/40 py-2 rounded text-xs font-bold transition flex justify-center items-center" onclick="window.saveChanges()"><i class="fa-solid fa-cloud-arrow-up mr-1"></i> 固化逻辑并提交审计</button></div>`;
        }
        document.getElementById('details-content').innerHTML = headerHtml + bodyHtml;
        if (itemType === 'link' && currentSelectedData.evidences) { const slider = document.getElementById('final-conf-slider'); const display = document.getElementById('final-conf-display'); if (slider && display) slider.addEventListener('input', (e) => { display.innerText = parseFloat(e.target.value).toFixed(2); }); }
    }

    window.saveChanges = async () => {
        if(!currentSelectedData) return;
        const btn = document.getElementById('save-btn'); const noteInput = document.getElementById('analyst-note-input').value.trim(); let updateDesc = []; let logEntry = { time: new Date().toLocaleString(), user: "分析师 (04291)", action: "研判更新", detail: "", reason: noteInput || "无备注" };
        if (currentItemType === 'node') {
            const riskSelect = document.getElementById('input-risk').value; if (currentSelectedData.risk !== riskSelect) { updateDesc.push(`威胁等级: [${currentSelectedData.risk||'未知'}] → [${riskSelect}]`); currentSelectedData.risk = riskSelect; }
            const statusSelect = document.getElementById('input-status').value; if ((currentSelectedData.status || 'UNKNOWN') !== statusSelect) { updateDesc.push(`状态调整: [${currentSelectedData.status || 'UNKNOWN'}] → [${statusSelect}]`); currentSelectedData.status = statusSelect; }
            const tagsInput = document.getElementById('input-tags').value.trim(); const currentTags = (currentSelectedData.tags || []).join(', '); if (currentTags !== tagsInput) { updateDesc.push(`标签更新: [${currentTags || '无'}] → [${tagsInput || '无'}]`); currentSelectedData.tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : []; }
            const aliasesInput = document.getElementById('input-aliases').value.trim(); const currentAliases = (currentSelectedData.known_aliases || []).join(', '); if (currentAliases !== aliasesInput) { updateDesc.push(`别名更新: [${currentAliases || '无'}] → [${aliasesInput || '无'}]`); currentSelectedData.known_aliases = aliasesInput ? aliasesInput.split(',').map(t => t.trim()).filter(t => t) : []; }
        } else {
            const predicateInput = document.getElementById('input-predicate').value; if (currentSelectedData.predicate !== predicateInput) { updateDesc.push(`关系本体: [${currentSelectedData.predicate}] → [${predicateInput}]`); currentSelectedData.predicate = predicateInput; }
            if (currentSelectedData.evidences && currentSelectedData.evidences.length > 0) {
                const checkboxes = document.querySelectorAll('.evidence-checkbox'); const accepted = [], rejected = []; checkboxes.forEach(cb => { if (cb.checked) accepted.push(cb.dataset.evId); else rejected.push(cb.dataset.evId); });
                const finalConf = parseFloat(document.getElementById('final-conf-slider')?.value || currentSelectedData.conf); if (currentSelectedData.conf !== finalConf || rejected.length > 0) { updateDesc.push(`置信度调整: [${currentSelectedData.conf}] → [${finalConf}]`); updateDesc.push(`证据采纳: ${accepted.length}条, 驳回: ${rejected.length}条`); currentSelectedData.conf = finalConf; }
            }
        }
        if (updateDesc.length === 0 && !noteInput) return alert("未检测到更改内容");
        logEntry.detail = updateDesc.length > 0 ? updateDesc.join(" | ") : "添加了研判批注"; btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> 同步中...'; btn.disabled = true;
        try { await new Promise(resolve => setTimeout(resolve, 800)); currentSelectedData.audit_logs = currentSelectedData.audit_logs || []; currentSelectedData.audit_logs.unshift(logEntry); btn.innerHTML = '<i class="fa-solid fa-check"></i> 落库成功'; btn.classList.add('bg-green-500/20', 'text-green-500'); setTimeout(() => { openAnalystPanel(currentSelectedData, currentItemType); if (currentItemType === 'link') updateVisibility(); populateSidebar(); }, 600); } catch (error) { btn.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> 失败'; } finally { btn.disabled = false; }
    }

    window.openReportModal = () => {
        const tbody = document.getElementById('report-table-body'); tbody.innerHTML = ''; document.getElementById('report-generate-time').innerText = new Date().toLocaleString();
        fusionData.links.forEach(l => {
            const sN = getSafeNodeObj(l.source); const tN = getSafeNodeObj(l.target); const sName = sN ? (sN.name || sN.value || sN.label) : 'Unknown'; const tName = tN ? (tN.name || tN.value || tN.label) : 'Unknown'; let method = l.method || "智能图推断", hash = l.hash || "AI_INFERRED";
            let btnHtml = `<button class="text-[10px] px-2 py-1 bg-yellow-500/20 hover:bg-yellow-500/40 text-yellow-400 border border-yellow-500/50 rounded transition shadow-glow-warning whitespace-nowrap" onclick="window.closeReportModal(); window.findAndShow('${l.evidence_id}', 'link');"><i class="fa-solid fa-crosshairs"></i> 图谱定位</button>`;
            if (l.evidences && l.evidences.length > 0) { const ev = l.evidences[0]; const sourceInfo = fusionData.sourceRegistry[ev.source_id] || { name: ev.source_id }; method = `${sourceInfo.name} (${ev.method})`; if (ev.capsule && ev.capsule.snapshot) { hash = ev.capsule.snapshot.content_hash || hash; } btnHtml = `<button class="text-[10px] px-2 py-1 bg-primary/20 hover:bg-primary/40 text-primary border border-primary/50 rounded transition shadow-glow whitespace-nowrap" onclick="window.showRawEvidence('${l.evidence_id}', '${getSafeNodeId(l.source)}')"><i class="fa-solid fa-file-shield"></i> 调阅快照</button>`; }
            const cColor = l.conf >= 0.8 ? 'text-green-400' : (l.conf >= 0.5 ? 'text-warning' : 'text-danger'); const predZh = predicateMap[l.predicate]?.zh || l.predicate; const pathText = `<span class="text-white">${escapeHTML(sName)}</span> <i class="fa-solid fa-arrow-right text-gray-500 mx-1 text-[9px]"></i> <span class="text-primary font-bold">[${escapeHTML(predZh)}]</span> <i class="fa-solid fa-arrow-right text-gray-500 mx-1 text-[9px]"></i> <span class="text-white">${escapeHTML(tName)}</span>`;
            tbody.innerHTML += `<tr class="hover:bg-white/5 transition border-b border-white/5"><td class="font-mono text-gray-300 text-[10px] py-2 px-3">${escapeHTML(l.timestamp || '未知时间')}</td><td class="font-mono text-primary text-[10px] py-2 px-3">${escapeHTML(l.evidence_id)}</td><td class="text-xs py-2 px-3">${pathText}</td><td class="text-gray-300 text-[10px] py-2 px-3">${escapeHTML(method)}</td><td class="text-center font-bold text-xs py-2 px-3 ${cColor}">${Number(l.conf).toFixed(2)}</td><td class="font-mono text-gray-500 text-[9px] py-2 px-3 max-w-[120px] truncate" title="${escapeHTML(hash)}">${escapeHTML(hash)}</td><td class="text-center py-2 px-3">${btnHtml}</td></tr>`;
        }); toggleModal('report-modal', true);
    };

    window.exportReportCSV = () => {
        let csvContent = "data:text/csv;charset=utf-8,\uFEFF"; csvContent += "发现时间,证据编号,起点实体,动作/谓词,终点实体,采集方式/来源,置信度,源数据哈希校验\n";
        fusionData.links.forEach(l => {
            const sN = getSafeNodeObj(l.source); const tN = getSafeNodeObj(l.target); const sName = sN ? (sN.name || sN.value || sN.label) : 'Unknown'; const tName = tN ? (tN.name || tN.value || tN.label) : 'Unknown'; const predZh = predicateMap[l.predicate]?.zh || l.predicate; let method = l.method || "智能图推断", hash = l.hash || "AI_INFERRED";
            if (l.evidences && l.evidences.length > 0) { const ev = l.evidences[0]; const sourceInfo = fusionData.sourceRegistry[ev.source_id] || { name: ev.source_id }; method = `${sourceInfo.name} (${ev.method})`; if (ev.capsule && ev.capsule.snapshot) { hash = ev.capsule.snapshot.content_hash || hash; } }
            const row = [l.timestamp || '未知时间', l.evidence_id, sName, predZh, tName, method, Number(l.conf).toFixed(2), hash].map(v => `"${String(v).replace(/"/g, '""')}"`).join(","); csvContent += row + "\n";
        });
        const encodedUri = encodeURI(csvContent); const link = document.createElement("a"); link.setAttribute("href", encodedUri); link.setAttribute("download", `法庭证据链清单_${new Date().getTime()}.csv`); document.body.appendChild(link); link.click(); document.body.removeChild(link);
    };

    window.switchEvidenceTab = (tab) => {
        const isSnap = tab === 'snapshot'; document.getElementById('ev-tab-snapshot').classList.toggle('active', isSnap); document.getElementById('ev-pane-snapshot').classList.toggle('hidden', !isSnap); document.getElementById('ev-tab-llm').classList.toggle('active', !isSnap); document.getElementById('ev-pane-llm').classList.toggle('hidden', isSnap);
        if (!isSnap) { setTimeout(() => { document.querySelectorAll('.intent-bar').forEach(bar => bar.style.width = bar.getAttribute('data-target-width')); }, 50); }
    };

    window.showRawEvidence = (evidenceId, sourceNodeId = null) => {
        let targetEv = null; for(let l of fusionData.links) { if(l.evidences) { let found = l.evidences.find(e => e.evidence_id === evidenceId); if(found) { targetEv = found; break; } } }
        if (targetEv && targetEv.capsule) { 
            currentExtractionSourceId = sourceNodeId || getSafeNodeId(targetEv.source) || fusionData.nodes[0].id; const snapPane = document.getElementById('ev-pane-snapshot'); const llmPane = document.getElementById('ev-pane-llm'); const tabLlm = document.getElementById('ev-tab-llm'); const snap = targetEv.capsule.snapshot || {}; const jsonStr = JSON.stringify(targetEv.capsule, null, 2);
            if (snap.type === 'IMAGE' || snap.type === 'OCR') {
                const imgUrl = snap.url || '/offline/evidence-snapshot.svg'; const ocrText = snap.ocr_text ? `<div class="mt-4 p-3 bg-black/50 border border-primary/30 rounded text-xs text-primary font-mono"><div class="text-[10px] text-gray-500 mb-1 border-b border-white/10 pb-1">OCR / QR 解析提取内容:</div><div class="whitespace-pre-wrap">${escapeHTML(snap.ocr_text)}</div></div>` : '';
                snapPane.innerHTML = `<div class="w-1/2 border-r border-white/10 p-4 flex flex-col bg-black/50"><h3 class="text-xs font-bold text-gray-400 mb-2"><i class="fa-regular fa-image text-primary"></i> 原始多模态物证快照</h3><div class="flex-1 border border-white/20 rounded bg-black/80 flex items-center justify-center overflow-hidden relative group"><img src="${imgUrl}" class="max-w-full max-h-full object-contain group-hover:scale-105 transition-transform duration-500 shadow-lg"><div class="absolute inset-0 border border-primary/50 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div></div>${ocrText}</div><div class="w-1/2 p-4 overflow-y-auto custom-scrollbar bg-black"><h3 class="text-xs font-bold text-gray-400 mb-2"><i class="fa-solid fa-code text-green-400"></i> JSON 元数据 (Metadata)</h3><pre class="text-xs text-green-400 font-mono whitespace-pre-wrap break-all p-3 border border-green-500/30 bg-green-900/10 rounded">${escapeHTML(jsonStr)}</pre></div>`;
            } else { snapPane.innerHTML = `<div class="w-full p-4 overflow-y-auto custom-scrollbar bg-black"><h3 class="text-xs font-bold text-gray-400 mb-2"><i class="fa-solid fa-code text-green-400"></i> JSON 元数据 (Metadata)</h3><pre class="text-xs text-green-400 font-mono whitespace-pre-wrap break-all p-4 border border-green-500/30 bg-green-900/10 rounded">${escapeHTML(jsonStr)}</pre></div>`; }

            if (targetEv.capsule.llm_mock) {
                tabLlm.classList.remove('hidden'); const llmData = targetEv.capsule.llm_mock; window.currentLlmEntities = JSON.parse(JSON.stringify(llmData.entities));
                let highlightedText = escapeHTML(llmData.raw_text); llmData.entities.forEach(ent => { const safeTerm = escapeHTML(ent.highlight); const hlClass = ent.type === 'user' ? 'llm-hl-user' : (ent.type === 'wallet' ? 'llm-hl-wallet' : 'llm-hl-material'); const icon = ent.type === 'user' ? 'fa-user-secret' : (ent.type === 'wallet' ? 'fa-coins' : 'fa-box-open'); const regex = new RegExp(safeTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'); highlightedText = highlightedText.replace(regex, `<span class="${hlClass}" title="实体: ${escapeHTML(ent.value)} [${escapeHTML(ent.role)}]"><i class="fa-solid ${icon} text-[10px] mr-1 opacity-70"></i>$&</span>`); });
                const intentsHtml = llmData.intents.map(int => `<div class="mb-2.5"><div class="flex justify-between items-center text-[10px] mb-1"><span class="text-gray-300 font-bold">${escapeHTML(int.label)}</span><span class="text-gray-400 font-mono">${(int.score * 100).toFixed(1)}%</span></div><div class="intent-bar-container"><div class="intent-bar ${int.color}" style="width: 0%;" data-target-width="${int.score * 100}%"></div></div></div>`).join('');
                llmPane.innerHTML = `<div class="w-3/5 border-r border-white/10 p-5 flex flex-col bg-black/50"><h3 class="text-xs font-bold text-gray-400 mb-3 flex items-center gap-2"><i class="fa-solid fa-align-left text-primary"></i> 原始非结构化文本 (截获内容)</h3><div class="flex-1 bg-black p-4 rounded-lg border border-white/5 text-xs text-gray-300 leading-relaxed font-mono whitespace-pre-wrap overflow-y-auto custom-scrollbar shadow-inner">${highlightedText}</div></div><div class="w-2/5 p-5 overflow-y-auto custom-scrollbar bg-black/80 flex flex-col relative"><div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-green-500 to-primary"></div><h3 class="text-xs font-bold text-green-400 mb-4 flex items-center gap-2"><i class="fa-solid fa-microchip"></i> 情报意图解析 (Intent Classification)</h3><div class="bg-black/50 border border-white/5 p-3 rounded-lg mb-6 shadow-inner">${intentsHtml}</div><h3 class="text-xs font-bold text-primary mb-3 flex items-center gap-2"><i class="fa-solid fa-cube"></i> 图谱实体抽取 (NER Extraction)</h3><div id="llm-entities-container" class="flex-1 overflow-y-auto custom-scrollbar pr-1"></div><button class="mt-4 w-full bg-green-500/20 hover:bg-green-500/40 border border-green-500/50 text-green-400 py-2.5 rounded shadow-[0_0_15px_rgba(34,197,94,0.2)] hover:shadow-glow-green transition-all transform hover:scale-[1.02] flex items-center justify-center gap-2 text-xs font-bold" onclick="window.injectLLMEntities()"><i class="fa-solid fa-bolt"></i> 采纳抽取结果，一键固化入图</button><div class="mt-4 border-2 border-dashed border-gray-600 rounded-lg p-3 text-center cursor-pointer hover:border-primary text-gray-400 hover:text-primary transition group" onclick="window.simulateEvidenceUpload()"><i class="fa-solid fa-cloud-arrow-up text-lg mb-1 group-hover:-translate-y-1 transition-transform"></i><div class="text-[10px] font-bold">补充第三方证据 (Human-in-the-loop)</div><div class="text-[9px] opacity-70">支持 .pdf, .docx, .eml 等格式</div></div></div>`;
                window.renderLlmEntities(); window.switchEvidenceTab('llm');
            } else { tabLlm.classList.add('hidden'); window.switchEvidenceTab('snapshot'); }
            toggleModal('raw-evidence-modal', true);
        } else { alert("该关联边是由多源证据融合或智能推断生成，暂无绑定的单一底层取证包快照。"); }
    };

    window.triggerBatchLLMSandbox = () => {
        window.closeManualEntry(); window.showEngineLoader("批量案卷智能解析中...", "提取多模态文件特征，执行深度文本分析与 NER...");
        setTimeout(() => {
            window.hideEngineLoader();
            const mockExtractedText = "最新情报截获：嫌疑人通过电报群联系买家，指定使用XMR钱包地址 88AABBCCDDEEFF99 接收款项，并安排了 10kg 的管制前体发往东南亚某港口。备用联络人TG：@ShadowOps22。";
            window.currentLlmEntities = [ { type: "wallet", value: "88AABBCCDDEEFF99", role: "收款钱包", highlight: "88AABBCCDDEEFF99", isHumanEdited: false }, { type: "user", value: "@ShadowOps22", role: "马仔/接头人", highlight: "@ShadowOps22", isHumanEdited: false }, { type: "material", value: "管制前体 10kg", role: "违禁品", highlight: "10kg 的管制前体", isHumanEdited: false } ];
            const llmPane = document.getElementById('ev-pane-llm'); const snapPane = document.getElementById('ev-pane-snapshot'); const tabLlm = document.getElementById('ev-tab-llm');
            const jsonStr = JSON.stringify({ source_type: "User_Uploaded_File", file_hash: "sha256:abcd1234efgh5678", process_time: new Date().toISOString(), status: "PARSED_SUCCESS", ai_confidence_score: 0.94 }, null, 2);
            snapPane.innerHTML = `<div class="w-full p-4 overflow-y-auto custom-scrollbar bg-black"><h3 class="text-xs font-bold text-gray-400 mb-2"><i class="fa-solid fa-code text-green-400"></i> JSON 元数据 (本地文件)</h3><pre class="text-xs text-green-400 font-mono whitespace-pre-wrap break-all p-4 border border-green-500/30 bg-green-900/10 rounded">${escapeHTML(jsonStr)}</pre></div>`;
            let highlightedText = escapeHTML(mockExtractedText); window.currentLlmEntities.forEach(ent => { const safeTerm = escapeHTML(ent.highlight); const hlClass = ent.type === 'user' ? 'llm-hl-user' : (ent.type === 'wallet' ? 'llm-hl-wallet' : 'llm-hl-material'); const icon = ent.type === 'user' ? 'fa-user-secret' : (ent.type === 'wallet' ? 'fa-coins' : 'fa-box-open'); const regex = new RegExp(safeTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'); highlightedText = highlightedText.replace(regex, `<span class="${hlClass}" title="实体: ${escapeHTML(ent.value)} [${escapeHTML(ent.role)}]"><i class="fa-solid ${icon} text-[10px] mr-1 opacity-70"></i>$&</span>`); });
            llmPane.innerHTML = `<div class="w-3/5 border-r border-white/10 p-5 flex flex-col bg-black/50"><h3 class="text-xs font-bold text-gray-400 mb-3 flex items-center gap-2"><i class="fa-solid fa-file-import text-primary"></i> 原始非结构化文本 (本地解析)</h3><div class="flex-1 bg-black p-4 rounded-lg border border-white/5 text-xs text-gray-300 leading-relaxed font-mono whitespace-pre-wrap overflow-y-auto custom-scrollbar shadow-inner">${highlightedText}</div></div><div class="w-2/5 p-5 overflow-y-auto custom-scrollbar bg-black/80 flex flex-col relative"><div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-green-500 to-primary"></div><h3 class="text-xs font-bold text-green-400 mb-4 flex items-center gap-2"><i class="fa-solid fa-microchip"></i> 情报意图解析 (Intent Classification)</h3><div class="bg-black/50 border border-white/5 p-3 rounded-lg mb-6 shadow-inner"><div class="mb-2.5"><div class="flex justify-between items-center text-[10px] mb-1"><span class="text-gray-300 font-bold">黑灰产交易 (Black Market)</span><span class="text-gray-400 font-mono">96.5%</span></div><div class="intent-bar-container"><div class="intent-bar bg-purple-500" style="width: 0%;" data-target-width="96.5%"></div></div></div><div class="mb-2.5"><div class="flex justify-between items-center text-[10px] mb-1"><span class="text-gray-300 font-bold">涉黑物流 (Smuggling)</span><span class="text-gray-400 font-mono">88.2%</span></div><div class="intent-bar-container"><div class="intent-bar bg-blue-500" style="width: 0%;" data-target-width="88.2%"></div></div></div></div><h3 class="text-xs font-bold text-primary mb-3 flex items-center gap-2"><i class="fa-solid fa-cube"></i> 图谱实体抽取 (NER Extraction)</h3><div id="llm-entities-container" class="flex-1 overflow-y-auto custom-scrollbar pr-1"></div><button class="mt-4 w-full bg-green-500/20 hover:bg-green-500/40 border border-green-500/50 text-green-400 py-2.5 rounded shadow-[0_0_15px_rgba(34,197,94,0.2)] hover:shadow-glow-green transition-all transform hover:scale-[1.02] flex items-center justify-center gap-2 text-xs font-bold" onclick="window.injectLLMEntities()"><i class="fa-solid fa-bolt"></i> 人工审查无误，一键固化入图</button></div>`;
            currentExtractionSourceId = fusionData.nodes[0].id; tabLlm.classList.remove('hidden'); window.renderLlmEntities(); window.switchEvidenceTab('llm'); toggleModal('raw-evidence-modal', true); document.getElementById('batch-file-upload').value = '';
        }, 1500);
    };

    window.renderLlmEntities = () => {
        const container = document.getElementById('llm-entities-container'); if(!container) return;
        container.innerHTML = window.currentLlmEntities.map((ent, idx) => {
            const isEdited = ent.isHumanEdited; const textCol = isEdited ? 'text-orange-400' : (ent.type === 'user' ? 'text-primary' : (ent.type === 'wallet' ? 'text-warning' : 'text-material')); const borderCol = isEdited ? 'border-orange-500/50' : (ent.type === 'user' ? 'border-primary/50' : (ent.type === 'wallet' ? 'border-warning/50' : 'border-material/50')); const icon = ent.type === 'user' ? 'fa-user-secret' : (ent.type === 'wallet' ? 'fa-coins' : 'fa-box-open');
            const badgeHtml = isEdited ? `<span class="text-[9px] bg-orange-500/20 text-orange-400 border border-orange-500/30 px-1.5 py-0.5 rounded flex items-center gap-1 shadow-[0_0_8px_rgba(249,115,22,0.5)]"><i class="fa-solid fa-user-check"></i> 人工修正</span>` : `<span class="text-[9px] bg-green-500/20 text-green-400 border border-green-500/30 px-1.5 py-0.5 rounded">High Conf</span>`;
            return `<div class="bg-black/40 border border-white/10 hover:${borderCol} p-2 rounded mb-2 transition flex items-center justify-between group relative"><div class="flex items-center gap-2 w-full"><div class="w-6 h-6 rounded bg-white/5 border border-white/10 flex items-center justify-center ${textCol} text-[10px]"><i class="fa-solid ${icon}"></i></div><div class="flex-1 min-w-0 pr-2"><div class="text-xs font-bold text-white group-hover:${textCol} transition truncate">${escapeHTML(ent.value)}</div><div class="text-[9px] text-gray-500 truncate">${escapeHTML(ent.type)} / ${escapeHTML(ent.role || '实体')}</div></div></div><div class="flex items-center gap-2 shrink-0"><button class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-white transition text-[10px] bg-white/10 px-1.5 py-1 rounded" onclick="window.editLlmEntity(${idx})" title="人工修正字段"><i class="fa-solid fa-pen"></i></button>${badgeHtml}</div></div>`;
        }).join('');
    };

    window.editLlmEntity = (idx) => {
        const ent = window.currentLlmEntities[idx]; const newVal = prompt("请输入修正后的实体标识/名称:", ent.value);
        if(newVal !== null && newVal.trim() !== "") { const newType = prompt("请输入修正后的实体类型 (如 user, wallet, material, traffic):", ent.type); if(newType !== null && newType.trim() !== "") { ent.value = newVal.trim(); ent.type = newType.trim().toLowerCase(); ent.isHumanEdited = true; ent.role = ent.role || '人工标注'; window.renderLlmEntities(); window.showIntelToast("实体已完成人工修正，置信度将锁定为 1.0。", "success"); } }
    };

    window.simulateEvidenceUpload = () => { window.showIntelToast('正在解析第三方证据包...', 'info'); setTimeout(() => { window.showIntelToast('第三方证据上传完毕，已通过 Hash 校验并自动关联至当前证据容器。', 'success'); }, 1500); };

    window.injectLLMEntities = () => {
        const sourceNodeId = currentExtractionSourceId; const nowStr = new Date().toISOString().replace('T', ' ').substring(0, 16); let addedCount = 0;
        const newEntities = window.currentLlmEntities.map(ent => { return { id: 'llm_' + ent.type + '_' + Date.now() + Math.floor(Math.random()*100), type: ent.type, name: ent.type === 'user' ? ent.value : undefined, value: ent.value, role: ent.role, label: ent.type !== 'user' ? ent.value : undefined, risk: 'HIGH', tags: ent.isHumanEdited ? ["人工修正", "HITL录入"] : ["文件智能提取"], avatar: ent.type === 'user' ? '/offline/avatar-default.svg' : undefined, provenance: { source: ent.isHumanEdited ? "分析师介入 (HITL)" : "文件解析提纯", time: nowStr } }; });
        newEntities.forEach((ent, idx) => {
            const originalEnt = window.currentLlmEntities[idx]; const exists = fusionData.nodes.find(n => n.value === ent.value || n.name === ent.name);
            if (!exists) { fusionData.nodes.push(ent); fusionData.links.push({ source: sourceNodeId, target: ent.id, type: ent.type === 'user' ? 'command' : (ent.type === 'wallet' ? 'finance' : 'material'), predicate: ent.type === 'user' ? 'INSTRUCT' : (ent.type === 'wallet' ? 'ASSET_TRANSFER' : 'ITEM_PURCHASE'), evidence_id: "LLM-GEN-" + Math.floor(Math.random()*10000), timestamp: nowStr, method: originalEnt.isHumanEdited ? "分析师验证上传" : "文件解析生成", conf: originalEnt.isHumanEdited ? 1.0 : 0.95 }); addedCount++; }
        });
        if (addedCount > 0) { preprocessData(); initGraph(); toggleModal('raw-evidence-modal', false); window.showIntelToast(`⚡ LLM 提纯并入库完成！成功将 ${addedCount} 个实体验证并固化至画布。`, 'success'); } else { toggleModal('raw-evidence-modal', false); window.showIntelToast(`实体特征已存在于图谱中，未重复添加。`, 'info'); }
    };
    
    let currentEntryType = 'node';

    window.openManualEntry = () => {
        toggleModal('manual-entry-modal', true);
        let nodeOptions = fusionData.nodes.map(n => `<option value="${n.id}">${escapeHTML(n.name || n.label || n.value)}</option>`).join('');
        document.getElementById('new-link-source').innerHTML = nodeOptions; document.getElementById('new-link-target').innerHTML = nodeOptions;
        let predicateOptions = Object.keys(predicateMap).map(p => `<option value="${p}">${escapeHTML(predicateMap[p].zh)} (${p})</option>`).join('');
        document.getElementById('new-link-predicate').innerHTML = predicateOptions;
        window.updateSubtypeOptions(); window.switchEntryTab('node');
    };

    window.switchEntryTab = (type) => {
        currentEntryType = type; const isNode = type === 'node'; const isLink = type === 'link'; const isBatch = type === 'batch';
        document.getElementById('tab-add-node').className = `flex-1 py-1.5 text-xs rounded border font-bold transition ${isNode ? 'bg-blue-600 text-white border-blue-500' : 'bg-black/40 text-gray-400 border-white/10 hover:text-white'}`;
        document.getElementById('tab-add-link').className = `flex-1 py-1.5 text-xs rounded border font-bold transition ${isLink ? 'bg-blue-600 text-white border-blue-500' : 'bg-black/40 text-gray-400 border-white/10 hover:text-white'}`;
        document.getElementById('tab-add-batch').className = `flex-1 py-1.5 text-xs rounded border font-bold transition ${isBatch ? 'bg-blue-600 text-white border-blue-500' : 'bg-black/40 text-gray-400 border-white/10 hover:text-white'}`;
        document.getElementById('form-add-node').classList.toggle('hidden', !isNode); document.getElementById('form-add-link').classList.toggle('hidden', !isLink); document.getElementById('form-add-batch').classList.toggle('hidden', !isBatch);
        const submitBtn = document.getElementById('manual-entry-submit-btn'); if (submitBtn) { submitBtn.classList.toggle('hidden', isBatch); }
    };
    
    window.submitManualEntry = () => {
        if (currentEntryType === 'batch') return; 
        const now = new Date(); const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
        if (currentEntryType === 'node') {
            const category = document.getElementById('new-node-category').value; const subtype = document.getElementById('new-node-subtype').value; const value = document.getElementById('new-node-value').value; const source = document.getElementById('new-node-source').value;
            if (!value) return alert('请输入实体标识/名称');
            let iconLabel = category === 'user' ? '' : (category === 'wallet' ? '💰 ' : (category === 'traffic' ? '📍 ' : '🏷️ '));
            const newNode = { id: 'm_' + Math.random().toString(36).substr(2, 9), type: category, subtype: subtype, name: category === 'user' ? value : undefined, label: category !== 'user' ? `${iconLabel}${value}` : undefined, value: value, risk: "HIGH", score: 80, tags: ["人工标记"], avatar: "/offline/avatar-default.svg", provenance: { source: source || "分析师录入", method: "HUMINT/研判", time: timeStr, reliability: "A" }, audit_logs: [] };
            newNode.audit_logs.push({ time: new Date().toLocaleString(), user: "分析师 (04291)", action: "节点创建", detail: "分析师人工录入新实体", reason: "外部情报输入" }); fusionData.nodes.push(newNode);
        } else {
            const sId = document.getElementById('new-link-source').value, tId = document.getElementById('new-link-target').value; const predicate = document.getElementById('new-link-predicate').value, conf = parseFloat(document.getElementById('new-link-conf').value);
            if (sId === tId) return alert('起点和终点不能相同');
            const newLink = { source: sId, target: tId, type: predicateMap[predicate]?.type || 'command', predicate: predicate, evidence_id: "MANUAL-" + Math.floor(Math.random()*10000), timestamp: timeStr, method: "分析师人工研判", hash: "N/A (人工)", conf: conf, audit_logs: [] };
            newLink.audit_logs.push({ time: new Date().toLocaleString(), user: "分析师 (04291)", action: "关联创建", detail: `建立人工推演边: [${predicate}]`, reason: "情报孤岛连接" }); fusionData.links.push(newLink);
        }
        toggleModal('manual-entry-modal', false); initGraph();
    };

    // 初始化加载第一个剧本数据
    window.triggerScenarioLoad('narcotics');
});

onUnmounted(() => {
    if (window.simulation) window.simulation.stop();
});
</script>

<style scoped>
/* ====== 完全复刻原生 CSS 并兼容 Vue 动态 DOM ====== */
.topology-wrapper { font-family: 'Inter', 'Microsoft YaHei', sans-serif; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0b1b38; }
::-webkit-scrollbar-thumb { background: #102546; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #00f0ff; }

.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

.bg-grid { background-image: linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px); background-size: 40px 40px; }

/* 必须使用 :deep() 穿透，因为 D3 的元素是在 Vue 模板之外动态生成的 */
:deep(.node) { cursor: pointer; transition: filter 0.3s; }
:deep(.node:hover) { filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.8)); }
:deep(.node.brush-selected circle) { stroke: #00f0ff !important; stroke-width: 4px !important; filter: drop-shadow(0 0 15px rgba(0, 240, 255, 0.8)); }

:deep(.link) { fill: none; transition: stroke-width 0.2s, stroke 0.2s, opacity 0.5s, stroke-dasharray 0.3s; cursor: pointer; }
:deep(.link:hover) { stroke-opacity: 1 !important; opacity: 1 !important; filter: drop-shadow(0 0 5px rgba(255,255,255,0.7)); }

:deep(.link-finance) { stroke: #ffcc00; animation: flow 1s linear infinite; }
:deep(.link-logistics) { stroke: #007aff; }
:deep(.link-command) { stroke: #ff3b30; }
:deep(.link-material) { stroke: #bd00ff; }
:deep(.link-traffic) { stroke: #ff9500; }
:deep(.link-referral) { stroke: #d946ef; animation: flow 2s linear infinite reverse; }
@keyframes flow { from { stroke-dashoffset: 8; } to { stroke-dashoffset: 0; } }

:deep(.verdict-card) { background: linear-gradient(135deg, rgba(255, 59, 48, 0.15) 0%, rgba(13, 29, 58, 0.95) 100%); border: 1px solid rgba(255, 59, 48, 0.4); box-shadow: 0 0 20px rgba(255, 59, 48, 0.15); position: relative; }
:deep(.verdict-card::before) { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #ff3b30; transition: background-color 0.3s;}
:deep(.verdict-card.theme-terror::before) { background: #ff3b30; } :deep(.verdict-card.theme-smuggle::before) { background: #007aff; } :deep(.verdict-card.theme-narcotics::before) { background: #bd00ff; } :deep(.verdict-card.theme-dynamic::before) { background: #00f0ff; }

:deep(.analyst-input) { background: rgba(11, 27, 56, 0.95); border: 1px solid rgba(255,255,255,0.1); color: #a0b1c5; font-family: 'Consolas', monospace; padding: 4px 8px; border-radius: 4px; width: 100%; transition: all 0.2s; }
:deep(.analyst-input:focus) { outline: none; border-color: #00f0ff; background: rgba(0, 240, 255, 0.05); color: #00f0ff; }
:deep(.analyst-input[readonly]), :deep(.analyst-input:disabled) { border-color: rgba(255,255,255,0.05); color: #64748b; cursor: not-allowed; opacity: 0.8; }
:deep(select.analyst-input option) { background-color: #051029; color: #a0b1c5; }

:deep(.grade-badge) { font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 2px; border: 1px solid rgba(255,255,255,0.2); }
:deep(.grade-A) { background: #16a34a; color: #fff; border-color: #15803d; } 
:deep(.grade-B) { background: #2563eb; color: #fff; border-color: #1d4ed8; } 
:deep(.grade-C) { background: #ca8a04; color: #fff; border-color: #a16207; } 
:deep(.grade-D) { background: #d97706; color: #fff; border-color: #b45309; } 
:deep(.grade-E) { background: #dc2626; color: #fff; border-color: #b91c1c; } 
:deep(.grade-F) { background: #4b5563; color: #fff; border-color: #374151; } 

.panel-slide { transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1); }

:deep(.report-table th) { background: #102546; border: 1px solid #1e3a8a; padding: 10px; text-align: left; }
:deep(.report-table td) { border: 1px solid #1e3a8a; padding: 10px; font-size: 12px; }
:deep(.report-table tr:nth-child(even)) { background: rgba(0, 240, 255, 0.02); }
:deep(.report-table tr:hover) { background: rgba(0, 240, 255, 0.08); }

:deep(.status-dot) { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; box-shadow: 0 0 4px currentColor; }
:deep(.status-LIVE) { background-color: #22c55e; color: #22c55e; animation: pulse-dot 2s infinite; }
:deep(.status-ARCHIVED) { background-color: #eab308; color: #eab308; }
:deep(.status-DEGRADED) { background-color: #ef4444; color: #ef4444; }
@keyframes pulse-dot { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.2); } 100% { opacity: 1; transform: scale(1); } }

:deep(.tab-btn) { padding: 8px 16px; font-size: 12px; font-weight: bold; color: #a0b1c5; border-bottom: 2px solid transparent; transition: all 0.2s; cursor: pointer; outline: none; }
:deep(.tab-btn.active) { color: #00f0ff; border-bottom-color: #00f0ff; background: rgba(0, 240, 255, 0.05); }
:deep(.tab-btn:hover:not(.active)) { color: white; background: rgba(255,255,255,0.05); }

:deep(.ev-tab) { padding: 8px 20px; font-size: 12px; font-weight: bold; color: #64748b; border-bottom: 2px solid transparent; transition: all 0.2s; cursor: pointer; }
:deep(.ev-tab.active) { color: #00f0ff; border-bottom-color: #00f0ff; }
:deep(.ev-tab:hover:not(.active)) { color: white; }

:deep(.cluster-line) { width: 2px; background: rgba(255,255,255,0.1); position: absolute; top: 15px; bottom: 0; left: 15px; z-index: 0; }
:deep(.cluster-node) { position: relative; z-index: 1; }

#engine-loader { backdrop-filter: blur(10px); }
.loader-bar { width: 0%; height: 2px; background: #00f0ff; transition: width 0.5s ease; box-shadow: 0 0 10px #00f0ff; }

/* LLM Highlighter Styles */
:deep(.llm-hl-user) { background: rgba(0, 240, 255, 0.15); color: #00f0ff; border: 1px solid rgba(0, 240, 255, 0.5); padding: 0 4px; border-radius: 4px; cursor: pointer; transition: all 0.2s; }
:deep(.llm-hl-user:hover) { background: rgba(0, 240, 255, 0.3); box-shadow: 0 0 8px rgba(0, 240, 255, 0.6); }
:deep(.llm-hl-wallet) { background: rgba(255, 204, 0, 0.15); color: #ffcc00; border: 1px solid rgba(255, 204, 0, 0.5); padding: 0 4px; border-radius: 4px; cursor: pointer; transition: all 0.2s; }
:deep(.llm-hl-wallet:hover) { background: rgba(255, 204, 0, 0.3); box-shadow: 0 0 8px rgba(255, 204, 0, 0.6); }
:deep(.llm-hl-material) { background: rgba(189, 0, 255, 0.15); color: #bd00ff; border: 1px solid rgba(189, 0, 255, 0.5); padding: 0 4px; border-radius: 4px; cursor: pointer; transition: all 0.2s; }
:deep(.llm-hl-material:hover) { background: rgba(189, 0, 255, 0.3); box-shadow: 0 0 8px rgba(189, 0, 255, 0.6); }

:deep(.intent-bar-container) { background: rgba(0,0,0,0.5); border-radius: 10px; overflow: hidden; height: 6px; margin-top: 4px; }
:deep(.intent-bar) { height: 100%; border-radius: 10px; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); }
</style>