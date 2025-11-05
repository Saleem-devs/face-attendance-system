"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { apiGet, apiPost } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { ChevronDownIcon } from "lucide-react";

type Stats = {
  total_students: number;
  marked_today: number;
  attendance_rate_today: number;
};

type AttendanceRow = {
  id: number;
  student_id: string;
  student_name?: string;
  name?: string;
  attendance_time?: string;
  timestamp: string;
};

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | undefined>();
  const [attendance, setAttendance] = useState<AttendanceRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(
    new Date()
  );
  const formatApiDate = (d: Date) => {
    const y = d.getFullYear();
    const m = `${d.getMonth() + 1}`.padStart(2, "0");
    const dd = `${d.getDate()}`.padStart(2, "0");
    return `${y}-${m}-${dd}`;
  };
  const formatDisplayDate = (d?: Date) => {
    if (!d) return "Select date";
    const day = `${d.getDate()}`.padStart(2, "0");
    const month = `${d.getMonth() + 1}`.padStart(2, "0");
    const y = d.getFullYear();
    return `${day}/${month}/${y}`;
  };

  useEffect(() => {
    async function load() {
      try {
        await apiGet("/api/auth/me");
        const s = await apiGet("/api/stats");
        setStats(s);
        const d = selectedDate ? selectedDate : new Date();
        const att = await apiGet(`/api/attendance?date=${formatApiDate(d)}`);
        setAttendance(att.data || att);
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "Failed to load";
        setError(msg);
        if (msg.toLowerCase().includes("unauthorized") || msg.includes("401")) {
          router.replace("/");
          return;
        }
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [selectedDate]);

  return (
    <div className="min-h-dvh px-4 py-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <p className="text-sm text-muted-foreground">Overview</p>
        </div>
        <Button
          variant="secondary"
          onClick={async () => {
            try {
              await apiPost("/api/auth/logout");
              toast.success("Logged out");
              router.replace("/");
            } catch (e: unknown) {
              const msg = e instanceof Error ? e.message : "Failed";
              toast.error(msg);
            }
          }}
        >
          Logout
        </Button>
      </div>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Total students</p>
          <p className="text-2xl font-semibold">
            {stats?.total_students ?? "-"}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Marked today</p>
          <p className="text-2xl font-semibold">{stats?.marked_today ?? "-"}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Attendance rate</p>
          <p className="text-2xl font-semibold">
            {stats ? `${stats.attendance_rate_today}%` : "-"}
          </p>
        </Card>
      </div>
      <Card className="p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-medium">Attendance Record</h2>
          <div className="flex items-center gap-3">
            <div className="hidden sm:block text-sm text-muted-foreground">
              Select date
            </div>
            <Popover open={open} onOpenChange={setOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-48 justify-between font-normal"
                >
                  {formatDisplayDate(selectedDate)}
                  <ChevronDownIcon className="h-4 w-4" />
                </Button>
              </PopoverTrigger>
              <PopoverContent
                className="w-auto overflow-hidden p-0"
                align="end"
              >
                <div className="p-2">
                  <Label htmlFor="date" className="px-1">
                    Date
                  </Label>
                </div>
                <Calendar
                  mode="single"
                  selected={selectedDate}
                  captionLayout="dropdown"
                  onSelect={(d) => {
                    setSelectedDate(d ?? new Date());
                    setOpen(false);
                  }}
                />
              </PopoverContent>
            </Popover>
          </div>
        </div>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Student</TableHead>
                <TableHead>ID</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={3}>Loading...</TableCell>
                </TableRow>
              ) : attendance.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} className="text-muted-foreground">
                    No records yet
                  </TableCell>
                </TableRow>
              ) : (
                attendance.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell>
                      {r.attendance_time ||
                        new Date(r.timestamp).toLocaleTimeString()}
                    </TableCell>
                    <TableCell>{r.student_name || r.name}</TableCell>
                    <TableCell>{r.student_id}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </Card>
    </div>
  );
}
