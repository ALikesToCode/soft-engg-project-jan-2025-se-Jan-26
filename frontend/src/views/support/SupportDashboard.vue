<template>
    <div class="p-6">
      <div class="flex justify-end mb-4">
        <button class="bg-red-700 text-white px-4 py-2 rounded hover:bg-red-800">
          Filter
        </button>
      </div>
  
      <div class="bg-white shadow-lg rounded-lg overflow-hidden">
        <table class="min-w-full border border-gray-300">
          <thead class="bg-red-700 text-white">
            <tr>
              <th class="px-4 py-2 text-left">ID</th>
              <th class="px-4 py-2 text-left">Event Name</th>
              <th class="px-4 py-2 text-left">Status</th>
              <th class="px-4 py-2 text-left">Status Code</th>
              <th class="px-4 py-2 text-left">End Point</th>
              <th class="px-4 py-2 text-left">Date and Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(event, index) in eventLogs" :key="index" class="border-b hover:bg-gray-100">
              <td class="px-4 py-2">{{ event.id }}</td>
              <td class="px-4 py-2">{{ event.eventName }}</td>
              <td class="px-4 py-2">
                <span :class="{'text-green-600': event.status === 'Success', 'text-red-600': event.status === 'Failed'}">
                  {{ event.status }}
                </span>
              </td>
              <td class="px-4 py-2">{{ event.statusCode }}</td>
              <td class="px-4 py-2">{{ event.endPoint || '—' }}</td>
              <td class="px-4 py-2">{{ event.dateTime || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        eventLogs: [
          { id: 123456, eventName: 'Lorem Ipsum', status: 'Success', statusCode: 200, endPoint: '', dateTime: '' },
          { id: 123456, eventName: 'Lorem Ipsum', status: 'Failed', statusCode: 500, endPoint: '', dateTime: '' },
          { id: 123456, eventName: 'Lorem Ipsum', status: 'Success', statusCode: 201, endPoint: '', dateTime: '' },
          { id: 123456, eventName: 'Lorem Ipsum', status: 'Failed', statusCode: 400, endPoint: '', dateTime: '' }
        ]
      };
    }
  };
  </script>
  
  <style scoped>
  </style>
  