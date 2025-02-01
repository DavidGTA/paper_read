<template>
  <div class="knowledge-graph-container">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索论文..."
        class="search-input"
        @keyup.enter="searchPapers"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <el-button type="primary" @click="showAddPaperDialog">
        添加论文
      </el-button>
      <el-button type="primary" @click="showAddRelationDialog">
        添加论文关系
      </el-button>
      <el-button type="primary" @click="showRelationTypeManager">
        管理关系类型
      </el-button>
    </div>

    <!-- 图谱容器 -->
    <div id="cy" class="graph-container"></div>

    <!-- 节点详情侧边栏 -->
    <el-drawer
      v-model="drawerVisible"
      title="论文详情"
      direction="rtl"
      size="30%"
    >
      <template v-if="selectedNode">
        <h3>{{ selectedNode.title }}</h3>
        <p><strong>作者：</strong>{{ selectedNode.authors }}</p>
        <p><strong>摘要：</strong>{{ selectedNode.abstract }}</p>
        <p><strong>笔记：</strong>{{ selectedNode.notes }}</p>
        
        <el-divider />
        
        <h4>相关论文</h4>
        <el-table :data="relatedPapers" style="width: 100%">
          <el-table-column prop="title" label="论文标题" />
          <el-table-column prop="relationType" label="关系类型" width="120" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="showEditRelationDialog(row)">
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="deleteRelation(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-drawer>

    <!-- 添加论文对话框 -->
    <el-dialog
      v-model="addPaperDialogVisible"
      title="添加论文"
      width="50%"
    >
      <el-form :model="newPaper" label-width="100px">
        <el-form-item label="标题">
          <el-input v-model="newPaper.title" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="newPaper.authors" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="newPaper.abstract" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="笔记">
          <el-input v-model="newPaper.notes" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addPaperDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addPaper">确定</el-button>
      </template>
    </el-dialog>

    <!-- 添加关系对话框 -->
    <el-dialog
      v-model="addRelationDialogVisible"
      title="添加论文关系"
      width="50%"
    >
      <el-form :model="newRelation" label-width="120px">
        <el-form-item label="源论文">
          <el-select v-model="newRelation.source_paper_id" filterable placeholder="选择源论文">
            <el-option
              v-for="paper in papers"
              :key="paper.id"
              :label="paper.title"
              :value="paper.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="目标论文">
          <el-select v-model="newRelation.target_paper_id" filterable placeholder="选择目标论文">
            <el-option
              v-for="paper in papers"
              :key="paper.id"
              :label="paper.title"
              :value="paper.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关系类型">
          <el-select v-model="newRelation.relation_type_id" placeholder="选择关系类型">
            <el-option
              v-for="type in relationTypes"
              :key="type.id"
              :label="type.name"
              :value="type.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addRelationDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addRelation">确定</el-button>
      </template>
    </el-dialog>

    <!-- 关系类型管理对话框 -->
    <el-dialog
      v-model="relationTypeManagerVisible"
      title="关系类型管理"
      width="60%"
    >
      <relation-type-manager />
    </el-dialog>

    <!-- 编辑关系对话框 -->
    <el-dialog
      v-model="editRelationDialogVisible"
      title="编辑论文关系"
      width="50%"
    >
      <el-form :model="editingRelation" label-width="120px">
        <el-form-item label="关系类型">
          <el-select v-model="editingRelation.relation_type_id" placeholder="选择关系类型">
            <el-option
              v-for="type in relationTypes"
              :key="type.id"
              :label="type.name"
              :value="type.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editRelationDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="updateRelation">确定</el-button>
      </template>
    </el-dialog>
  </div>

  
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import cytoscape from 'cytoscape'
import axios from 'axios'
import RelationTypeManager from './RelationTypeManager.vue'

const cy = ref(null)
const searchKeyword = ref('')
const drawerVisible = ref(false)
const selectedNode = ref(null)
const addPaperDialogVisible = ref(false)
const newPaper = ref({
  title: '',
  authors: '',
  abstract: '',
  notes: ''
})
const relatedPapers = ref([])

const papers = ref([])
const relationTypes = ref([])
const addRelationDialogVisible = ref(false)
const relationTypeManagerVisible = ref(false)
const newRelation = ref({
  source_paper_id: null,
  target_paper_id: null,
  relation_type_id: null
})

const editRelationDialogVisible = ref(false)
const editingRelation = ref({
  id: null,
  relation_type_id: null,
  source_paper_id: null,
  target_paper_id: null
})

// 加载论文列表
async function loadPapers() {
  try {
    const response = await axios.get('http://localhost:8000/api/v1/papers')
    papers.value = response.data
  } catch (error) {
    console.error('加载论文列表失败:', error)
  }
}

// 加载关系类型列表
async function loadRelationTypes() {
  try {
    const response = await axios.get('http://localhost:8000/api/v1/relation-types')
    relationTypes.value = response.data
  } catch (error) {
    console.error('加载关系类型失败:', error)
  }
}

// 添加论文关系
async function addRelation() {
  try {
    await axios.post('http://localhost:8000/api/v1/paper-relations', newRelation.value)
    addRelationDialogVisible.value = false
    newRelation.value = {
      source_paper_id: null,
      target_paper_id: null,
      relation_type_id: null
    }
    await loadData() // 重新加载图谱数据
    ElMessage.success('添加关系成功')
  } catch (error) {
    console.error('添加关系失败:', error)
    ElMessage.error('添加关系失败')
  }
}

function showAddRelationDialog() {
  loadPapers()
  loadRelationTypes()
  addRelationDialogVisible.value = true
}

function showRelationTypeManager() {
  relationTypeManagerVisible.value = true
}

// 添加颜色映射函数
const getRelationTypeColor = (typeId) => {
  // 为不同的关系类型定义不同的颜色
  const colors = {
    1: '#FF6B6B', // 引用关系
    2: '#4ECDC4', // 扩展关系
    3: '#45B7D1', // 相似研究
    4: '#96CEB4', // 同作者
    default: '#666666'
  }
  return colors[typeId] || colors.default
}

// 初始化图谱
onMounted(() => {
  cy.value = cytoscape({
    container: document.getElementById('cy'),
    elements: [],
    style: [
      {
        selector: 'node',
        style: {
          'background-color': '#4a90e2',
          'label': 'data(label)',
          'width': 80,
          'height': 80,
          'font-size': '12px',
          'text-wrap': 'wrap',
          'text-max-width': 300,
          'text-valign': 'center',
          'text-halign': 'center',
          'text-overflow-wrap': 'break-word',
          'word-break': 'keep-all',
          'white-space': 'pre-wrap',
          'padding': '10px',
          'shape': 'round',
          'border-width': 2,
          'border-color': '#2171c1',
          'text-outline-color': '#fff',
          'text-outline-width': 2,
          'color': '#000',
          'overlay-padding': '6px',
          'z-index': 10
        }
      },
      {
        selector: 'node:selected',
        style: {
          'background-color': '#f39c12',
          'border-color': '#d35400',
          'border-width': 3,
          'shadow-blur': 10,
          'shadow-color': '#000',
          'shadow-opacity': 0.3,
          'shadow-offset-x': 0,
          'shadow-offset-y': 0
        }
      },
      {
        selector: 'node:active',
        style: {
          'overlay-color': '#000',
          'overlay-padding': '8px',
          'overlay-opacity': 0.2
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 3,
          'line-color': 'data(color)',
          'target-arrow-color': 'data(color)',
          'target-arrow-shape': 'vee',
          'arrow-scale': 1.5,
          'curve-style': 'bezier',
          'label': 'data(label)',
          'font-size': '11px',
          'text-rotation': 'autorotate',
          'text-margin-y': -10,
          'text-background-color': '#fff',
          'text-background-opacity': 0.8,
          'text-background-padding': '3px',
          'text-border-opacity': 0.8,
          'text-border-width': 1,
          'text-border-color': '#ccc'
        }
      },
      {
        selector: 'edge:selected',
        style: {
          'width': 4,
          'line-color': '#f39c12',
          'target-arrow-color': '#f39c12',
          'shadow-blur': 10,
          'shadow-color': '#000',
          'shadow-opacity': 0.3
        }
      }
    ],
    layout: {
      name: 'cose',
      animate: true,
      animationDuration: 500,
      refresh: 20,
      fit: true,
      padding: 30,
      randomize: true,
      nodeRepulsion: function(node) { return 100000; },
      nodeOverlap: 20,
      idealEdgeLength: function(edge) { return 150; },
      edgeElasticity: function(edge) { return 100; },
      nestingFactor: 1.2,
      gravity: 80,
      numIter: 1000,
      initialTemp: 200,
      coolingFactor: 0.95,
      minTemp: 1.0,
      weaver: false,
      nodeDimensionsIncludeLabels: true
    },
    wheelSensitivity: 0.3,
    minZoom: 0.3,
    maxZoom: 3
  })

  // 注册交互事件
  cy.value.on('tap', 'node', function(evt) {
    const node = evt.target
    selectedNode.value = {
      id: node.id(),
      title: node.data('label'),
      authors: node.data('authors'),
      abstract: node.data('abstract'),
      notes: node.data('notes')
    }
    loadRelatedPapers(node.id())
    drawerVisible.value = true
  })

  // 添加鼠标悬停效果
  cy.value.on('mouseover', 'node', function(evt) {
    const node = evt.target
    node.style({
      'border-width': 4,
      'shadow-blur': 10,
      'shadow-color': '#000',
      'shadow-opacity': 0.3
    })
  })

  cy.value.on('mouseout', 'node', function(evt) {
    const node = evt.target
    if (!node.selected()) {
      node.removeStyle()
    }
  })

  // 加载初始数据
  loadData()
})

// 修改 loadData 函数中的元素创建部分
async function loadData() {
  try {
    const [papersRes, relationsRes, relationTypesRes] = await Promise.all([
      axios.get('http://localhost:8000/api/v1/papers'),
      axios.get('http://localhost:8000/api/v1/paper-relations'),
      axios.get('http://localhost:8000/api/v1/relation-types')
    ])

    const elements = []
    
    // 添加节点
    papersRes.data.forEach(paper => {
      elements.push({
        data: {
          id: paper.id.toString(),
          label: paper.title,
          authors: paper.authors,
          abstract: paper.abstract,
          notes: paper.notes
        }
      })
    })

    // 创建关系类型到颜色的映射
    const relationTypeColors = {}
    relationTypesRes.data.forEach((type, index) => {
      relationTypeColors[type.id] = getRelationTypeColor(type.id)
    })

    // 添加边
    relationsRes.data.forEach(relation => {
      elements.push({
        data: {
          id: `e${relation.id}`,
          source: relation.source_paper_id.toString(),
          target: relation.target_paper_id.toString(),
          label: relation.relation_type_name,
          color: relationTypeColors[relation.relation_type_id]
        }
      })
    })

    cy.value.elements().remove()
    cy.value.add(elements)
    
    // 使用更适合的布局
    const layout = cy.value.layout({
      name: 'cose',
      animate: true,
      animationDuration: 500,
      refresh: 20,
      fit: true,
      padding: 50,
      nodeDimensionsIncludeLabels: true
    })
    
    layout.run()
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

// 加载相关论文
async function loadRelatedPapers(paperId) {
  try {
    const response = await axios.get(`http://localhost:8000/api/v1/paper-relations`)
    relatedPapers.value = response.data
      .filter(r => r.source_paper_id.toString() === paperId || r.target_paper_id.toString() === paperId)
      .map(r => ({
        id: r.id,
        title: r.source_paper_id.toString() === paperId ? r.target_paper_title : r.source_paper_title,
        relationType: r.relation_type_name,
        relation_type_id: r.relation_type_id,
        source_paper_id: r.source_paper_id,
        target_paper_id: r.target_paper_id,
        isSource: r.source_paper_id.toString() === paperId
      }))
  } catch (error) {
    console.error('加载相关论文失败:', error)
    ElMessage.error('加载相关论文失败')
  }
}

// 添加新论文
async function addPaper() {
  try {
    const response = await axios.post('http://localhost:8000/api/v1/papers', newPaper.value)
    addPaperDialogVisible.value = false
    await loadData()
    newPaper.value = { title: '', authors: '', abstract: '', notes: '' }
  } catch (error) {
    console.error('添加论文失败:', error)
  }
}

// 搜索论文
function searchPapers() {
  if (!searchKeyword.value) {
    cy.value.elements().show()
    return
  }

  cy.value.elements().hide()
  cy.value.nodes().filter(node => {
    return node.data('label').toLowerCase().includes(searchKeyword.value.toLowerCase())
  }).forEach(node => {
    node.show()
    node.neighborhood().show()
  })
}

function showAddPaperDialog() {
  addPaperDialogVisible.value = true
}

// 显示编辑关系对话框
function showEditRelationDialog(row) {
  editingRelation.value = {
    id: row.id,
    relation_type_id: row.relation_type_id,
    source_paper_id: row.source_paper_id,
    target_paper_id: row.target_paper_id
  }
  loadRelationTypes()
  editRelationDialogVisible.value = true
}

// 更新关系
async function updateRelation() {
  try {
    await axios.put(
      `http://localhost:8000/api/v1/paper-relations/${editingRelation.value.id}`,
      {
        source_paper_id: editingRelation.value.source_paper_id,
        target_paper_id: editingRelation.value.target_paper_id,
        relation_type_id: editingRelation.value.relation_type_id
      }
    )
    editRelationDialogVisible.value = false
    await loadRelatedPapers(selectedNode.value.id)
    await loadData() // 重新加载图谱
    ElMessage.success('更新关系成功')
  } catch (error) {
    console.error('更新关系失败:', error)
    ElMessage.error('更新关系失败')
  }
}

// 删除关系
async function deleteRelation(row) {
  try {
    await ElMessageBox.confirm('确定要删除这个关系吗？', '提示', {
      type: 'warning'
    })
    await axios.delete(`http://localhost:8000/api/v1/paper-relations/${row.id}`)
    await loadRelatedPapers(selectedNode.value.id)
    await loadData() // 重新加载图谱
    ElMessage.success('删除关系成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除关系失败:', error)
      ElMessage.error('删除关系失败')
    }
  }
}
</script>

<style scoped>
.knowledge-graph-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
}

.toolbar {
  padding: 16px;
  display: flex;
  gap: 16px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 100;
}

.search-input {
  width: 300px;
}

.graph-container {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  margin: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  overflow: hidden;
}
</style> 