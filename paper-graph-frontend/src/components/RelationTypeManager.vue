<template>
  <div>
    <el-button type="primary" @click="showAddDialog">
      添加关系类型
    </el-button>

    <el-table :data="relationTypes" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="关系类型名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="showEditDialog(row)">
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑关系类型' : '添加关系类型'"
      width="40%"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const relationTypes = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({
  name: '',
  description: ''
})

// 加载关系类型数据
const loadRelationTypes = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/v1/relation-types')
    relationTypes.value = response.data
  } catch (error) {
    ElMessage.error('加载关系类型失败')
  }
}

// 显示添加对话框
const showAddDialog = () => {
  isEdit.value = false
  form.value = { name: '', description: '' }
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  try {
    if (isEdit.value) {
      await axios.put(`http://localhost:8000/api/v1/relation-types/${form.value.id}`, form.value)
      ElMessage.success('更新成功')
    } else {
      await axios.post('http://localhost:8000/api/v1/relation-types', form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadRelationTypes()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '添加失败')
  }
}

// 删除关系类型
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个关系类型吗？', '提示', {
      type: 'warning'
    })
    await axios.delete(`http://localhost:8000/api/v1/relation-types/${row.id}`)
    ElMessage.success('删除成功')
    loadRelationTypes()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadRelationTypes()
})
</script>