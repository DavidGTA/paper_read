<template>
  <el-config-provider :locale="zhCn">
    <knowledge-graph />
  </el-config-provider>
</template>

<script setup>
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
</script>

<style>
body {
  margin: 0;
  padding: 0;
}
</style> 