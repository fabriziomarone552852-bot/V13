// frontend/src/hooks/uiMonth/useMonthModals.ts
import { useTaskModals } from '@/context/TaskModalContext';
import { useEventModals } from '@/context/EventModalContext';

export const useMonthModals = () => {
  const taskModals = useTaskModals();
  const eventModals = useEventModals();

  return {
    // Eventi
    isDetailOpen: eventModals.isDetailOpen,
    closeEventDetail: eventModals.closeEventDetail,
    selectedEvent: eventModals.selectedEvent,
    openEventDetail: eventModals.openEventDetail,
    isFormOpen: eventModals.isFormOpen,
    closeEventForm: eventModals.closeEventForm,
    openEventForm: eventModals.openEventForm,
    eventToEdit: eventModals.eventToEdit,
    initialDate: eventModals.initialDate,
    // Task
    openTaskDetail: taskModals.openTaskDetail,
    openTaskForm: taskModals.openTaskForm,
  };
};