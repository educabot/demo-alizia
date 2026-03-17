import * as React from 'react';
import * as TabsPrimitive from '@radix-ui/react-tabs';
import { cn } from '@/lib/utils';

const TabsCustom = TabsPrimitive.Root;

const TabsCustomList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn('inline-flex items-center gap-2 p-1 rounded-xl bg-[#F7F9FD99]', className)}
    {...props}
  />
));
TabsCustomList.displayName = TabsPrimitive.List.displayName;

const TabsCustomTrigger = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Trigger
    ref={ref}
    className={cn(
      'cursor-pointer inline-flex items-center justify-center whitespace-nowrap rounded-lg px-2 py-1 headline-2-semi-bold transition-all focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50',
      'text-[#92A3BB]',
      'data-[state=active]:bg-white data-[state=active]:text-[#735fe3] data-[state=active]:shadow-sm',
      className,
    )}
    {...props}
  />
));
TabsCustomTrigger.displayName = TabsPrimitive.Trigger.displayName;

const TabsCustomContent = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn(
      'mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
      className,
    )}
    {...props}
  />
));
TabsCustomContent.displayName = TabsPrimitive.Content.displayName;

export { TabsCustom, TabsCustomList, TabsCustomTrigger, TabsCustomContent };
