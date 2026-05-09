<template>
  <div class="home-page">
    <PageHeader
      :now-time="nowTime"
      :selected-subscription="selectedSubscription"
      :subscriptions="subscriptions"
      @navigate="goTo"
      @logout="logoutToLogin"
      @update:subscription="selectedSubscription = $event; applySubscription()"
    />

    <Toast :visible="toastVisible" :message="toastMessage" />

    <div class="main-container">
      <CaseList
        :warnings="filteredWarnings"
        :status-filter="warningStatusFilter"
        @update:statusFilter="warningStatusFilter = $event"
        @show-detail="showWarningDetail"
      />

      <StatsOverview
        :warning-count="warningCount"
        :handled-count="handledCount"
        :total-count="totalCount"
        :now-time-display="nowTimeDisplay"
        :selected-type="selectedType"
        :time-filter="statsTimeFilter"
        :sa-items="saStatsItems"
        :sa-summary="saSummary"
        :sa-loading="saStatsLoading"
        :sa-error="saStatsError"
        :filtered-sa-items="filteredSaItems"
        @update:selectedType="selectedType = $event"
        @update:timeFilter="statsTimeFilter = $event"
      />

      <TrendChart
        :type-filter="trendTypeFilter"
        :range-filter="trendRangeFilter"
        @update:typeFilter="trendTypeFilter = $event"
        @update:rangeFilter="trendRangeFilter = $event"
      />

      <PersonTrackList
        :persons="filteredPersons"
        :selected-type="selectedType"
        :avatar-initial="avatarInitial"
        :score-class="scoreClass"
        @update:selectedType="selectedType = $event"
        @view-all="personsModalVisible = true"
        @show-detail="showPersonDetail"
      />

      <MonitoredTicker
        :entities="monitoredEntities"
        :avatar-initial="avatarInitial"
      />

      <ThreatMap
        :scene="mapScene"
        :mode="mapMode"
        :warnings="warnings"
        :country-coordinates="countryCoordinates"
        :selected-subscription="selectedSubscription"
        :subscriptions="subscriptions"
        @update:scene="mapScene = $event"
        @update:mode="mapMode = $event"
        @country-click="handleMapClick"
        @context-menu="handleContextMenu"
      />

      <LiveFeedCluster
        :feed="filteredFeed"
        @view-all="eventsModalVisible = true"
        @show-detail="showFeedDetail"
      />

      <PageFooter />
    </div>

    <DetailModal
      :visible="detailVisible"
      :title="detailTitle"
      :mode="detailMode"
      :person="currentPerson"
      :html-content="detailHtml"
      :avatar-initial="avatarInitial"
      :score-class="scoreClass"
      @close="closeDetailModal"
      @clone="openCloneWorkspace"
    />

    <EventsListModal
      :visible="eventsModalVisible"
      :events="warnings"
      @close="eventsModalVisible = false"
      @show-detail="showWarningDetail"
    />

    <PersonsListModal
      :visible="personsModalVisible"
      :persons="personsTableRows"
      :country="personsModalCountry"
      @close="personsModalVisible = false"
      @show-detail="showPersonDetail"
      @clone="openCloneWorkspace"
    />

    <OrgListModal
      :visible="orgModalVisible"
      :country="orgCountry"
      :tab="orgTab"
      :risk-filter="orgRiskFilter"
      :orgs="filteredOrgRows"
      @close="orgModalVisible = false"
      @update:tab="orgTab = $event"
      @update:riskFilter="orgRiskFilter = $event"
    />

    <CountryEventsModal
      :visible="countryEventsModalVisible"
      :title="countryEventsTitle"
      :events="countryEventRows"
      @close="countryEventsModalVisible = false"
      @show-detail="showWarningDetail"
    />

    <CloneWorkspaceModal
      :visible="cloneWorkspaceVisible"
      :target="cloneTarget"
      @close="cloneWorkspaceVisible = false"
    />

    <MapContextMenu
      :visible="mapContextVisible"
      :x="mapContextX"
      :y="mapContextY"
      :country="mapContextCountry"
      @close="mapContextVisible = false"
      @open-circle-menu="openCircleMenuAtContext"
      @open-drawer="showCountryDrawerFromMenu"
    />

    <CircleMenu
      :visible="circleMenuVisible"
      :x="circleMenuX"
      :y="circleMenuY"
      @close="circleMenuVisible = false"
      @open-drawer="showCountryDrawerFromMenu"
      @show-events="showCountryEventsList(mapContextCountry)"
      @show-persons="showPersonList(mapContextCountry)"
      @open-org-list="openOrgList(mapContextCountry)"
    />

    <CountryDrawer
      :visible="drawerVisible"
      :country="drawerCountry"
      :threat="drawerThreat"
      :count="drawerCount"
      :persons="drawerPersons"
      :events="drawerEvents"
      :score-class="scoreClass"
      @close="drawerVisible = false"
      @show-persons="showPersonList"
      @show-events="showCountryEventsList"
      @show-person="showPersonDetail"
      @show-event="showWarningDetail"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useHomeData } from '../composables/useHomeData';

// 组件导入
import PageHeader from '../components/home/PageHeader.vue';
import Toast from '../components/common/Toast.vue';
import CaseList from '../components/home/CaseList.vue';
import StatsOverview from '../components/home/StatsOverview.vue';
import TrendChart from '../components/home/TrendChart.vue';
import PersonTrackList from '../components/home/PersonTrackList.vue';
import MonitoredTicker from '../components/home/MonitoredTicker.vue';
import ThreatMap from '../components/home/ThreatMap.vue';
import LiveFeedCluster from '../components/home/LiveFeedCluster.vue';
import PageFooter from '../components/home/PageFooter.vue';
import DetailModal from '../components/home/DetailModal.vue';
import EventsListModal from '../components/home/EventsListModal.vue';
import PersonsListModal from '../components/home/PersonsListModal.vue';
import OrgListModal from '../components/home/OrgListModal.vue';
import CountryEventsModal from '../components/home/CountryEventsModal.vue';
import CloneWorkspaceModal from '../components/home/CloneWorkspaceModal.vue';
import MapContextMenu from '../components/home/MapContextMenu.vue';
import CircleMenu from '../components/home/CircleMenu.vue';
import CountryDrawer from '../components/home/CountryDrawer.vue';

// 使用 composable
const {
  // 时间
  nowTime,
  nowTimeDisplay,

  // Toast
  toastVisible,
  toastMessage,
  showToast,

  // 订阅
  subscriptions,
  selectedSubscription,

  // 筛选
  warningStatusFilter,
  selectedType,
  statsTimeFilter,
  trendTypeFilter,
  trendRangeFilter,

  // 数据
  warnings,
  filteredWarnings,
  warningCount,
  handledCount,
  totalCount,
  hotPersons,
  filteredPersons,
  feed,
  filteredFeed,
  monitoredEntities,
  countryCoordinates,
  orgRows,

  // SA 告警统计
  saStatsItems,
  saStatsTotal,
  saStatsLoading,
  saStatsError,
  filteredSaItems,
  saSummary,
  fetchSubscriptionAlertStats,

  // 弹窗状态
  detailVisible,
  detailTitle,
  detailHtml,
  detailMode,
  currentPerson,
  eventsModalVisible,
  personsModalVisible,
  personsModalCountry,
  orgModalVisible,
  orgCountry,
  orgTab,
  orgRiskFilter,
  countryEventsModalVisible,
  countryEventsTitle,
  mapContextVisible,
  mapContextX,
  mapContextY,
  mapContextCountry,
  circleMenuVisible,
  circleMenuX,
  circleMenuY,
  drawerVisible,
  drawerCountry,
  cloneWorkspaceVisible,
  cloneTarget,

  // 计算属性
  drawerPersons,
  drawerEvents,
  drawerThreat,
  drawerCount,
  filteredOrgRows,
  personsTableRows,
  countryEventRows,

  // 方法
  applySubscription,
  showWarningDetail,
  showPersonDetail,
  showFeedDetail,
  openOrgList,
  showCountryEventsList,
  showPersonList,
  showCountryDrawerFromMenu,
  openCircleMenuAtContext,
  openCloneWorkspace,
  goTo,
  logoutToLogin,
  avatarInitial,
  scoreClass,
  closeDetailModal,
  handleMapClick,
  handleContextMenu
} = useHomeData();

// 地图场景和模式
const mapScene = ref('global');
const mapMode = ref('world');
</script>

<style src="../assets/styles/pages/home.css"></style>
