

<template>
    <div class="flex h-screen">
        <div class="w-16 bg-gradient-to-b from-red-800 to-red-600 flex flex-col justify-center items-center p-2 text-white space-y-6">
            <div class="text-3xl"><router-link to="/user/dashboard"><i class="bi bi-menu-button-wide-fill hover:cursor-pointer"></i></router-link></div>
            <div class="text-3xl"><router-link to="/user/courses"><span class="hover:cursor-pointer">📜</span></router-link></div>
            <div class="text-3xl"><i class="bi bi-arrow-clockwise hover:cursor-pointer"></i></div>
        </div>
    </div>
</template>