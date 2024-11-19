def appearance(intervals):
    lesson_start, lesson_end = intervals['lesson']
    pupil_intervals = intervals['pupil']
    tutor_intervals = intervals['tutor']

    # Функция для слияния пересекающихся интервалов
    def merge_overlapping_intervals(intervals):
        if not intervals:
            return []

        # Сортируем интервалы по началу
        sorted_intervals = sorted(zip(intervals[::2], intervals[1::2]))
        merged = [sorted_intervals[0][0], sorted_intervals[0][1]]

        for start, end in sorted_intervals[1:]:
            # Если текущий интервал пересекается с последним слитым
            if start <= merged[-1]:
                # Обновляем конец последнего слитого интервала
                merged[-1] = max(merged[-1], end)
            else:
                # Добавляем новый интервал
                merged.extend([start, end])

        return merged

    # Находим интервалы присутствия в рамках урока
    def get_lesson_intervals(intervals):
        lesson_intervals = []
        for i in range(0, len(intervals), 2):
            start = max(lesson_start, intervals[i])
            end = min(lesson_end, intervals[i + 1])
            if start < end:
                lesson_intervals.extend([start, end])
        return lesson_intervals

    # Получаем интервалы присутствия для ученика и учителя
    pupil_lesson_intervals = get_lesson_intervals(pupil_intervals)
    tutor_lesson_intervals = get_lesson_intervals(tutor_intervals)

    # Объединяем интервалы ученика
    pupil_merged = merge_overlapping_intervals(pupil_lesson_intervals)
    # Объединяем интервалы учителя
    tutor_merged = merge_overlapping_intervals(tutor_lesson_intervals)

    # Находим пересечения интервалов
    common_intervals = []
    i, j = 0, 0
    while i < len(pupil_merged) and j < len(tutor_merged):
        start1, end1 = pupil_merged[i], pupil_merged[i + 1]
        start2, end2 = tutor_merged[j], tutor_merged[j + 1]

        # Находим пересечение интервалов
        start = max(start1, start2)
        end = min(end1, end2)

        if start < end:
            common_intervals.extend([start, end])

        # Двигаем указатель того интервала, который заканчивается раньше
        if end1 < end2:
            i += 2
        else:
            j += 2

    # Вычисляем общую длительность пересечений
    total_time = 0
    for i in range(0, len(common_intervals), 2):
        total_time += common_intervals[i + 1] - common_intervals[i]

    return total_time