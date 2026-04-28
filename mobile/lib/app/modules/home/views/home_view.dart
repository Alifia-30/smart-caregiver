import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/models/patient_model.dart';
import '../../../data/services/auth_service.dart';
import '../controllers/home_controller.dart';

class HomeView extends GetView<HomeController> {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: NestedScrollView(
          headerSliverBuilder: (_, __) => [
            SliverToBoxAdapter(child: _buildHeader()),
          ],
          body: RefreshIndicator(
            onRefresh: controller.loadPatients,
            color: AppColors.primary,
            child: _buildBody(),
          ),
        ),
      ),
      floatingActionButton: _buildFab(),
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  // ── Header ──────────────────────────────────────────────
  Widget _buildHeader() {
    final authService = Get.find<AuthService>();
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 24, 20, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(controller.greeting,
                      style: AppTextStyles.labelMd
                          .copyWith(color: AppColors.onSurfaceVariant)),
                  const SizedBox(height: 2),
                  Obx(() => Text(
                    'Hi, ${authService.userName ?? 'User'}!',
                    style: AppTextStyles.headlineLg,
                  )),
                ],
              ),
              _avatarButton(),
            ],
          ),
          const SizedBox(height: 16),
          // Subtitle
          Text(
            'Here is the status of your patients today.',
            style:
                AppTextStyles.bodyMd.copyWith(color: AppColors.onSurfaceVariant),
          ),
          const SizedBox(height: 20),
          // Upcoming visit card
          _upcomingCard(),
          const SizedBox(height: 20),
          // Search
          _searchBar(),
          const SizedBox(height: 20),
          // Section header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Your Patients', style: AppTextStyles.headlineMd),
              Obx(() => Text(
                    '${controller.filteredPatients.length} total',
                    style: AppTextStyles.labelSm,
                  )),
            ],
          ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }

  Widget _avatarButton() {
    return GestureDetector(
      onTap: () {},
      child: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: AppColors.primary,
          borderRadius: BorderRadius.circular(14),
        ),
        child: const Icon(Icons.person_outline_rounded,
            color: AppColors.onPrimary, size: 22),
      ),
    );
  }

  Widget _upcomingCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.primary,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(Icons.schedule_rounded,
                color: Colors.white, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Upcoming Visit',
                    style: AppTextStyles.labelSm
                        .copyWith(color: Colors.white70)),
                const SizedBox(height: 2),
                Text('Pak Budi — 10:30 AM',
                    style: AppTextStyles.bodyMd.copyWith(
                        color: Colors.white, fontWeight: FontWeight.w600)),
              ],
            ),
          ),
          const Icon(Icons.chevron_right_rounded,
              color: Colors.white70, size: 20),
        ],
      ),
    );
  }

  Widget _searchBar() {
    return TextField(
      controller: controller.searchController,
      onChanged: controller.onSearchChanged,
      style: AppTextStyles.bodyMd,
      decoration: InputDecoration(
        hintText: 'Search patients...',
        prefixIcon:
            const Icon(Icons.search_rounded, color: AppColors.outline, size: 20),
        suffixIcon: Obx(() => controller.searchQuery.isNotEmpty
            ? IconButton(
                icon: const Icon(Icons.close_rounded,
                    size: 18, color: AppColors.outline),
                onPressed: () {
                  controller.searchController.clear();
                  controller.onSearchChanged('');
                },
              )
            : const SizedBox.shrink()),
      ),
    );
  }

  // ── Body ─────────────────────────────────────────────────
  Widget _buildBody() {
    return Obx(() {
      if (controller.isLoading) {
        return const Center(
            child: CircularProgressIndicator(color: AppColors.primary));
      }
      final list = controller.filteredPatients;
      if (list.isEmpty) {
        return _emptyState();
      }
      return ListView.separated(
        padding: const EdgeInsets.fromLTRB(20, 0, 20, 100),
        itemCount: list.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (_, i) => _patientCard(list[i]),
      );
    });
  }

  Widget _emptyState() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.people_outline_rounded,
              size: 64, color: AppColors.outline.withValues(alpha: 0.5)),
          const SizedBox(height: 16),
          Text('No patients yet', style: AppTextStyles.headlineMd),
          const SizedBox(height: 8),
          Text('Tap + to add your first patient',
              style: AppTextStyles.bodyMd
                  .copyWith(color: AppColors.onSurfaceVariant)),
        ],
      ),
    );
  }

  Widget _patientCard(Patient patient) {
    final statusColors = [
      const Color(0xFF16A34A),
      const Color(0xFFF59E0B),
      const Color(0xFF2563EB),
    ];
    final idx = patient.id != null ? patient.id! % 3 : 0;
    final statusColor = statusColors[idx];

    return GestureDetector(
      onTap: () => controller.goToPatientDetail(patient),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surfaceLowest,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: AppColors.primary.withValues(alpha: 0.05),
              blurRadius: 12,
              offset: const Offset(0, 4),
            )
          ],
        ),
        child: Row(
          children: [
            // Avatar
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Center(
                child: Text(patient.initials,
                    style: AppTextStyles.labelMd.copyWith(
                        color: Colors.white, fontWeight: FontWeight.w700)),
              ),
            ),
            const SizedBox(width: 14),
            // Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(patient.name,
                      style: AppTextStyles.bodyMd
                          .copyWith(fontWeight: FontWeight.w600)),
                  const SizedBox(height: 4),
                  Text('Age ${patient.age}',
                      style: AppTextStyles.labelMd
                          .copyWith(color: AppColors.onSurfaceVariant)),
                ],
              ),
            ),
            // Status dot + chevron
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: statusColor,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(height: 8),
                Icon(Icons.chevron_right_rounded,
                    color: AppColors.outline.withValues(alpha: 0.5), size: 20),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFab() {
    return FloatingActionButton.extended(
      onPressed: controller.goToAddPatient,
      backgroundColor: AppColors.accent,
      foregroundColor: AppColors.onBackground,
      elevation: 2,
      icon: const Icon(Icons.person_add_rounded, size: 20),
      label: Text('Add Patient',
          style:
              AppTextStyles.labelMd.copyWith(fontWeight: FontWeight.w700)),
    );
  }

  Widget _buildBottomNav() {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceLowest,
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.06),
            blurRadius: 16,
            offset: const Offset(0, -4),
          )
        ],
      ),
      child: BottomNavigationBar(
        currentIndex: 0,
        onTap: (i) {},
        items: const [
          BottomNavigationBarItem(
              icon: Icon(Icons.home_rounded), label: 'Home'),
          BottomNavigationBarItem(
              icon: Icon(Icons.medical_services_outlined), label: 'Health'),
          BottomNavigationBarItem(
              icon: Icon(Icons.calendar_today_outlined), label: 'Schedule'),
          BottomNavigationBarItem(
              icon: Icon(Icons.person_outline_rounded), label: 'Profile'),
        ],
      ),
    );
  }
}
